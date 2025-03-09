import bme280_sensor
from mqtt_client import MQTTClient
from time import sleep
import paho.mqtt.publish as publish
from paho.mqtt.enums import MQTTProtocolVersion
import logging

logging.basicConfig(level=logging.INFO)

mqtt_client_instance = MQTTClient(host="localhost", port=1883)

while True:
    try:
        weather_data = bme280_sensor.get_all_data()
    except Exception as sensor_error:
        logging.error(f"Failed to retrieve sensor data! {sensor_error}")

    data = {
        "temp": weather_data.temperature,
        "temp_format": "C",
        "humidity": weather_data.humidity,
        "humidity_format": "%",
        "pressure": weather_data.pressure,
        "pressure_format": "hPa",
        "timestamp": weather_data.timestmap
    }

    mqtt_client_instance.publish("weather/data", data)

    print(weather_data)
    print('-------------------------------------------------')
    sleep(1)