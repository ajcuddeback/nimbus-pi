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
    _wind_speed_sensor = Button(5)
    _wind_count = 0
    curent_wind_speed = 0
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
            self._wind_speed_sensor.when_pressed = self.spin


    def run(self):
        self.running = True
        while self.running:
            time.sleep(self._sample_rate)
            triggers_per_second = self._wind_count / self._sample_rate
            self.curent_wind_speed = triggers_per_second * self._mph_per_switch
            self._wind_count = 0

    def stop(self):
        logger_instance.log.info("Shutting wind speed thread down")
        self.runing = False
        self._wind_speed_sensor.when_pressed = NotImplemented
        self._wind_count = 0
        self.curent_wind_speed = 0
    
    def spin(self):
        self._wind_count += 1
        logger_instance.log.info("spin " + str(self._wind_count))