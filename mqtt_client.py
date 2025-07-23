import paho.mqtt.client as mqtt
import json
from logger import Logger
from dotenv import load_dotenv
import os
import threading
import time

load_dotenv()
logger_instance = Logger(location=os.getenv('STATION_NAME'))

class MQTTClient:
    _instance = None
    _lock = threading.Lock()
    _station_id = ""

    def __new__(cls, *args, **kwargs):
        with cls._lock:  # Thread-safe singleton
            if cls._instance is None:
                cls._instance = super(MQTTClient, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, host='localhost', port=1883, keepalive=60):
        if self._initialized:
            return  # Already initialized, skip re-initialization

        self.client = mqtt.Client(protocol=mqtt.MQTTv5)
        self.client.enable_logger(logger_instance.log)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message

        self.host = host
        self.port = port
        self.keepalive = keepalive

        self._stop_loop = threading.Event()

        self.connect()

        self.loop_thread = threading.Thread(target=self._start_loop, daemon=True)
        self.loop_thread.start()

        self._initialized = True  # Mark as initialized

    def connect(self):
        try:
            self.client.connect(self.host, self.port, self.keepalive)
            logger_instance.log.info("Successfully connected to MQTT Client")

        except Exception as e:
            logger_instance.log.error(f"Initial connection failed: {e}")
            self._attempt_reconnect()

    def _start_loop(self):
        while not self._stop_loop.is_set():
            try:
                logger_instance.log.info("Starting MQTT loop_forever...")
                self.client.loop_forever()
            except Exception as e:
                logger_instance.log.error(f"MQTT loop crashed: {e}", exc_info=True)
                logger_instance.log.info("Retrying MQTT loop in 10 seconds...")
                time.sleep(10)        

    def _attempt_reconnect(self, max_attempts=5):
        for attempt in range(1, max_attempts + 1):
            try:
                logger_instance.log.warning(f"Reconnect attempt {attempt} of {max_attempts}")
                self.client.reconnect()
                logger_instance.log.info("Reconnection successful")
                return
            except Exception as e:
                logger_instance.log.error(f"Reconnect failed: {e}")
                time.sleep(5)

        critical_message = (
            f"CRITICAL: Failed to reconnect to MQTT Broker after {max_attempts} attempts. "
            "Service may be unstable. Manual intervention may be required."
        )
        logger_instance.log.critical(critical_message)
        raise ConnectionError(critical_message)
    
    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            logger_instance.log.info("Connected to MQTT Broker!")
            try:
                self.client.subscribe("stationId")
                logger_instance.log.info("Subscribed to topic: stationId")
            except Exception as e:
                logger_instance.log.error(f"Failed to subscribe: {e}")
        else:
            logger_instance.log.error(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        logger_instance.log.warning(f"Disconnected from MQTT Broker with code {rc}")

    def on_publish(self, client, userdata, mid):
        logger_instance.log.info(f"Message {mid} published successfully.")

    def publish(self, topic, payload, qos=1, retain=True):
        try:
            if not self.client.is_connected():
                logger_instance.log.warning("Client not connected. Skipping publish.")
                return

            logger_instance.log.info(f"Publishing to topic {topic}")
            result = self.client.publish(topic, json.dumps(payload), qos=qos, retain=retain)
            status = result.rc
            if status != mqtt.MQTT_ERR_SUCCESS:
                logger_instance.log.error(f"Failed to publish to {topic}: status {status}")
        except Exception as e:
            logger_instance.log.error(f"Exception during publish: {e}", exc_info=True)

    def on_message(self, client, userdata, msg):
        logger_instance.log.info(f"Received message on topic: {msg.topic} with payload: {msg.payload.decode()}")
        try: 
            if msg.topic == "stationId":
                logger_instance.log.info(f"Got the station id: {msg.payload.decode()}")
                self._station_id = msg.payload.decode()
        except Exception as e:
            logger_instance.log.error(f"Failure on subscription: {e}")

    def stop(self):
        logger_instance.log.info("Stopping MQTT client loop...")
        self._stop_loop.set()
        self.client.disconnect()
        self.loop_thread.join(timeout=10)        
