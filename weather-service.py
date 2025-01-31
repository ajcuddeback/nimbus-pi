import bme280_sensor
from time import sleep



while True:
    weather_data = bme280_sensor.get_all_data()
    print(weather_data)
    sleep(1)