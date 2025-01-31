import bme280
import smbus2
from time import sleep

port = 1
address = 0x76 # BME280 Address
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)

def get_all_data():
    return bme280.sample(bus, address)

def sample_temp():
    bme280_data = bme280.sample(bus,address)
    return (9/5) * bme280_data.temperature + 32

def sample_humidty():
    bme280_data = bme280.sample(bus,address)
    return bme280_data.humidity
     
def sample_pressure():
    bme280_data = bme280.sample(bus,address)
    return bme280_data.pressure