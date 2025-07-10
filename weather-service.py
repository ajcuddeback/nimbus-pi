import bme280_sensor
from mqtt_client import MQTTClient
from wind_direction import WindDirection
from wind import WindSpeed
from logger import Logger
from time import sleep
from dotenv import load_dotenv
import threading
import os

load_dotenv()
logger_instance = Logger(location=os.getenv('STATION_NAME'))

required_envs = ['STATION_LON', 'STATION_LAT', 'STATION_CITY', 'STATION_STATE', 'WEATHER_POLLING_RATE']
for var in required_envs:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing environment variable: {var}")

mqtt_client_instance = MQTTClient(host="localhost", port=1883)
wind_direction_singleton_instance = WindDirection()
wind_direction_thread = threading.Thread(target=wind_direction_singleton_instance.run)
wind_direction_thread.start()

wind_speed_singleton_instance = WindSpeed()
wind_speed_thread = threading.Thread(target=wind_speed_singleton_instance.run)
wind_speed_thread.start()

# Allow for wind direction to populate
sleep(5)

has_station_id = False

weather_station_data = {
    "lon": os.getenv("STATION_LON"),
    "lat": os.getenv("STATION_LAT"),
    "city": os.getenv("STATION_CITY"),
    "state": os.getenv("STATION_STATE")
}

logger_instance.log.info("Sending Station Id Request")
mqtt_client_instance.publish("stationId/request", weather_station_data)

weather_rate = int(os.getenv("WEATHER_POLLING_RATE"))

while True:
    if mqtt_client_instance._station_id == "":
        logger_instance.log.warning("Station ID not populated yet")
        sleep(2)
        continue

    try:
        logger_instance.log.info('Fetching data')
        weather_data = bme280_sensor.get_all_data()
        data = {
            "temp": round(weather_data.temperature, 2),
            "temp_format": "C",
            "hum": round(weather_data.humidity, 2),
            "pr": round(weather_data.pressure, 2),
            "pr_format": "hPa",
            "timestamp": round(weather_data.timestamp.timestamp()),
            "stationId": mqtt_client_instance._station_id,
            "wind_direction": wind_direction_singleton_instance.direction,
            "wind_speed": wind_speed_singleton_instance.curent_wind_speed,
            "wind_speed_format": "mph"
        }

        # mqtt_client_instance.publish("weather/data", data)
        logger_instance.log.info(data)
        logger_instance.log.info('-------------------------------------------------')

    except Exception as sensor_error:
        logger_instance.log.error(f"Failed to retrieve sensor data! {sensor_error}")
    except KeyboardInterrupt:
        wind_direction_singleton_instance.stop()
        wind_direction_thread.join()
        wind_speed_singleton_instance.stop()
        wind_speed_thread.join()
        logger_instance.log.info("Exiting gracefully")    

    sleep(weather_rate)