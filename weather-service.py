import bme280_sensor
from mqtt_client import MQTTClient
from time import sleep
import paho.mqtt.publish as publish
from paho.mqtt.enums import MQTTProtocolVersion
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

file_handler = logging.FileHandler('mqtt_logs.log');
file_handler.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

mqtt_client_instance = MQTTClient(host="localhost", port=1883)

while True:
    try:
        weather_data = bme280_sensor.get_all_data()
    except Exception as sensor_error:
        logger.error(f"Failed to retrieve sensor data! {sensor_error}")

    data = {
        "temp": round(weather_data.temperature, 2),
        "temp_format": "C",
        "hum": round(weather_data.humidity, 2),
        "pr": round(weather_data.pressure, 2),
        "pr_format": "hPa",
        "timestamp": round(weather_data.timestamp.timestamp())
    }

    mqtt_client_instance.publish("weather/data", data)

    print(weather_data)
    print('-------------------------------------------------')
    sleep(30)