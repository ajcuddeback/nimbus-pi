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
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

        self.host = host
        self.port = port
        self.keepalive = keepalive

        self.connect()
        self.client.loop_start()  # Start network loop in background thread

        self._initialized = True  # Mark as initialized

    def connect(self):
        try:
            self.client.connect(self.host, self.port, self.keepalive)
            logger_instance.log.info("Successfully connected to MQTT Client")
        except Exception as e:
            logger_instance.log.error(f"Initial connection failed: {e}")
            self.reconnect()

    def reconnect(self):
        reconnectAttempts = 5
        attemptsMade = 1
        while attemptsMade <= reconnectAttempts:
            try:
                logger_instance.log.info(f"Attempting to reconnect to MQTT Broker. Attempt {attemptsMade} of {reconnectAttempts}")
                self.client.reconnect()
                return
            except Exception as e:
                logger_instance.log.error(f"Reconnection attempt {attempts + 1} failed: {e}")
                attemptsMade += 1
                time.sleep(5)

        critical_message = (
            f"CRITICAL: Failed to reconnect to MQTT Broker after "
            f"{self.max_reconnect_attempts} attempts. "
            f"No weather data will be sent until service is restarted. "
            f"Check broker status and network connection immediately."
        )
        logger_instance.log.critical(critical_message)
        # Optionally raise an exception or exit
        raise ConnectionError(critical_message)

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            logger_instance.log.info("Connected to MQTT Broker!")
        else:
            logger_instance.log.error(f"Failed to connect, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        logger_instance.log.warning("Disconnected from MQTT Broker.")
        self.reconnect()

    def on_publish(self, client, userdata, mid):
        logger_instance.log.info(f"Message {mid} published successfully.")

    def publish(self, topic, payload, qos=1, retain=True):
        try:
            result = self.client.publish(topic, json.dumps(payload), qos=qos, retain=retain)
            status = result[0]
            if status != mqtt.MQTT_ERR_SUCCESS:
                logger_instance.log.error(f"Failed to publish message to {topic}: {status}")
        except Exception as e:
            logger_instance.log.error(f"Exception while publishing: {e}")
