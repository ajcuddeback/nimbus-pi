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
        "temp": round(weather_data.temperature, 2),
        "temp_format": "C",
        "humidity": round(weather_data.humidity, 2),
        "humidity_format": "%",
        "pressure": round(weather_data.pressure, 2),
        "pressure_format": "hPa",
        "timestamp": weather_data.timestamp.timestamp()
    }

    mqtt_client_instance.publish("weather/data", data)

    print(weather_data)
    print('-------------------------------------------------')
    sleep(30)