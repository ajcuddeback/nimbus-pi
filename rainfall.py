from gpiozero import Button
from signal import pause  # <- This keeps the script running
import time
import threading
import os
from dotenv import load_dotenv
from logger import Logger

load_dotenv()
logger_instance = Logger(location=os.getenv('STATION_NAME'))
class Rainfall:
    _instance = None
    _lock = threading.Lock()
    _rainfall_sensor = Button(6)
    _current_mm_count = 0
    _mm_per_tip = 0.2794

    def __new__(cls, *args, **kwargs):
        with cls._lock:  # Thread-safe singleton
            if cls._instance is None:
                cls._instance = super(Rainfall, cls).__new__(cls)
                cls._instance._initialized = False
                cls._instance.running = False
            return cls._instance
        
    def __init__(self):
        if not getattr(self, '_initialized', False):
            super().__init__()
            self.running = False
            self._initialized = True
            self._rainfall_sensor.when_pressed = self.count_up

    def run(self):
        self.running = True
       
    def stop(self):
        logger_instance.log.info("Shutting rainfall thread down")
        self.running = False
        self._rainfall_sensor.when_pressed = None
        self.reset_rainfall_count()

    def get_current_rainfall(self):
        return self._current_mm_count    
    
    def count_up(self):
        self._current_mm_count += self._mm_per_tip
        logger_instance.log.info("New mm count: " + str(self._current_mm_count))

    def reset_rainfall_count(self):
        self._current_mm_count = 0    