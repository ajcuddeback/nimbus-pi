import bme280_sensor
from mqtt_client import MQTTClient
from DFRobot_AS3935_ordinary import begin_lightning_detection
from wind_direction import WindDirection
from wind import WindSpeed
from rainfall import Rainfall
from logger import Logger
from time import sleep
from dotenv import load_dotenv
import threading
import os

def main():
    load_dotenv()
    logger_instance = Logger(location=os.getenv('STATION_NAME'))

    # Validate required env vars
    required_envs = ['STATION_LON', 'STATION_LAT', 'STATION_CITY', 'STATION_STATE', 'WEATHER_POLLING_RATE']
    for var in required_envs:
        if not os.getenv(var):
            raise EnvironmentError(f"Missing environment variable: {var}")

    mqtt_client_instance = MQTTClient(host="localhost", port=1883)

    wind_direction_instance = WindDirection()
    wind_speed_instance = WindSpeed()
    rainfall_instance = Rainfall()

    wind_direction_thread = threading.Thread(target=wind_direction_instance.run)
    wind_speed_thread = threading.Thread(target=wind_speed_instance.run)
    rainfall_thread = threading.Thread(target=rainfall_instance.run)

    wind_direction_thread.start()
    wind_speed_thread.start()
    rainfall_thread.start()

    try:
        logger_instance.log.info("Waiting for wind sensor to initialize...")
        sleep(5)

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

            begin_lightning_detection(mqtt_client_instance._station_id)
            logger_instance.log.info('Fetching data')
            weather_data = bme280_sensor.get_all_data()
            rainfall = rainfall_instance.get_current_rainfall()
            data = {
                "temp": round(weather_data.temperature, 2),
                "temp_format": "C",
                "hum": round(weather_data.humidity, 2),
                "pr": round(weather_data.pressure, 2),
                "pr_format": "hPa",
                "timestamp": round(weather_data.timestamp.timestamp()),
                "stationId": mqtt_client_instance._station_id,
                "wind_direction": wind_direction_instance.direction,
                "wind_speed": wind_speed_instance.curent_wind_speed,
                "wind_speed_format": "mph",
                "rainfall": rainfall,
                "rainfall_format": "mm"
            }
            rainfall_instance.reset_rainfall_count()

            mqtt_client_instance.publish("weather/data", data)

            logger_instance.log.info(data)
            logger_instance.log.info('-------------------------------------------------')
            sleep(weather_rate)

    except KeyboardInterrupt:
        logger_instance.log.info("KeyboardInterrupt received. Cleaning up...")

    finally:
        wind_direction_instance.stop()
        wind_speed_instance.stop()
        rainfall_instance.stop()

        wind_direction_thread.join(timeout=5)
        wind_speed_thread.join(timeout=5)
        rainfall_thread.join(timeout=5)

if __name__ == "__main__":
    main()