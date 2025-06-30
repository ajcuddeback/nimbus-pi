import bme280_sensor
from mqtt_client import MQTTClient
from logger import Logger
from time import sleep
from dotenv import load_dotenv
import os

load_dotenv()
logger_instance = Logger(location=os.getenv('STATION_NAME'))

mqtt_client_instance = MQTTClient(host="localhost", port=1883)

has_station_id = False

weather_station_data = {
    "coordinates": { "long": os.getenv('STATION_LONG'), "lat": os.getenv('STATION_LAT') },
    "lon": os.getenv("STATION_LON"),
    "lat": os.getenv("STATION_LAT"),
    "city": os.getenv("STATION_CITY"),
    "state": os.getenv("STATION_STATE")
}

logger_instance.log.info("Sending Station Id Request")
mqtt_client_instance.publish("stationId/request", weather_station_data)

while has_station_id == False:
    if mqtt_client_instance._station_id != "":
        has_station_id = False
    else: 
        has_station_id = True
    
    sleep(int(os.getenv('STATION_ID_POLLING_RATE')))    

while has_station_id == True:
    if mqtt_client_instance._station_id == "":
        has_station_id = False
        logger_instance.log.fatal("Station id doesn't exist!")


    try:
        weather_data = bme280_sensor.get_all_data()
    except Exception as sensor_error:
        logger_instance.error(f"Failed to retrieve sensor data! {sensor_error}")

    data = {
        "temp": round(weather_data.temperature, 2),
        "temp_format": "C",
        "hum": round(weather_data.humidity, 2),
        "pr": round(weather_data.pressure, 2),
        "pr_format": "hPa",
        "timestamp": round(weather_data.timestamp.timestamp()),
        "stationId": mqtt_client_instance._station_id
    }

    mqtt_client_instance.publish("weather/data", data)

    logger_instance.log.info(weather_data)
    logger_instance.log.info('-------------------------------------------------')
    sleep(int(os.getenv('WEATHER_POLLING_RATE')))