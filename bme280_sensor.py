import bme280
import smbus2
from time import sleep

port = 1
address = 0x76 # BME280 Address
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)

while True:
    bme280_data = bme280.sample(bus,address)
    humidity  = bme280_data.humidity
    pressure  = bme280_data.pressure
    ambient_temperature = (9/5) * bme280_data.temperature + 32
    print(humidity, pressure, ambient_temperature)
    sleep(1)