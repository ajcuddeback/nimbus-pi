import bme280_sensor
from time import sleep
import paho.mqtt.publish as publish
from paho.mqtt.enums import MQTTProtocolVersion
import logging

logging.basicConfig(level=logging.INFO)

while True:
    try:
        weather_data = bme280_sensor.get_all_data()
    except Exception as sensor_error:
        logging.error(f"Failed to retrieve sensor data! {sensor_error}")

    data = {
        "temp": weather_data.temperature,
        "temp_format": "C",
        "humidity": weather_data.humidty,
        "humidity_format": "%",
        "pressure": weather_data.pressure,
        "pressure_format": "hPa",
        "timestamp": weather_data.timestmap
    }

    # TODO: Instead of using the convienence function, instead using the more advanced setup which allows for more fine grained control https://pypi.org/project/paho-mqtt/
    try:
        publish.multiple(data, hostname="localhost", protocol=MQTTProtocolVersion.MQTTv5)
    except Exception as mqtt_error:
        logging.error(f"MQTT publish failed: {mqtt_error}")
    else:
        logging.info("Data published successfully.")

    print(weather_data)
    print('-------------------------------------------------')
    sleep(1)