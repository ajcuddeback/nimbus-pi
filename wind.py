from gpiozero import Button
from signal import pause  # <- This keeps the script running
import time
import threading
import os
from dotenv import load_dotenv
from logger import Logger

load_dotenv()
logger_instance = Logger(location=os.getenv('STATION_NAME'))
class WindSpeed:
    _instance = None
    _lock = threading.Lock()
    _wind_speed_lock = threading.Lock()
    _wind_speed_sensor = Button(5)
    _wind_count = 0
    _wind_speeds = []
    _mph_per_switch = 1.492
    _sample_rate = 5

    def __new__(cls, *args, **kwargs):
        with cls._lock:  # Thread-safe singleton
            if cls._instance is None:
                cls._instance = super(WindSpeed, cls).__new__(cls)
                cls._instance._initialized = False
                cls._instance.running = False
            return cls._instance
        
    def __init__(self):
        if not getattr(self, '_initialized', False):
            super().__init__()
            self.running = False
            self._initialized = True
            self._wind_speed_sensor.when_pressed = self._on_spin


    def run(self):
        self.running = True
        try:
            while self.running:
                time.sleep(self._sample_rate)
                triggers_per_second = self._wind_count / self._sample_rate
                self._wind_speeds.append(triggers_per_second * self._mph_per_switch)
                self._wind_count = 0
        except Exception as e:
            logger_instance.log.error(f"WindSpeed thread error: {e}")
        finally:
            logger_instance.log.info("WindSpeed thread exiting cleanly")

    def get_wind_speed_average(self):
        if not self._wind_speeds:
            return 0.0

        with self._wind_speed_lock:
            avg = sum(self._wind_speeds) / len(self._wind_speeds)
            self._wind_speeds.clear()
        return avg
       

    def stop(self):
        logger_instance.log.info("Shutting wind speed thread down")
        self.running = False
        self._wind_speed_sensor.when_pressed = None
        with self._wind_speed_lock:
            self._wind_count = 0
            self._wind_speeds.clear()
    
    def _on_spin(self):
        with self._wind_speed_lock:
            self._wind_count += 1
        # logger_instance.log.info("spin " + str(self._wind_count))