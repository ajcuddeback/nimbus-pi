import bme280_sensor
from mqtt_client import MQTTClient
from logger import Logger
from time import sleep
from dotenv import load_dotenv
import os
import paho.mqtt.publish as publish
from paho.mqtt.enums import MQTTProtocolVersion
import logging

load_dotenv()
logger_instance = Logger(location=os.getenv('STATION_NAME'))

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
        "timestamp": round(weather_data.timestamp.timestamp()),
        "coordinates": { "long": os.getenv('STATION_LONG'), "lat": os.getenv('STATION_LAT') },
        "station_name": os.getenv('STATION_NAME')
    }

    mqtt_client_instance.publish("weather/data", data)

    logger_instance.log.info(weather_data)
    logger_instance.log.info('-------------------------------------------------')
    sleep(30)