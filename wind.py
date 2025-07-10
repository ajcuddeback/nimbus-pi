from gpiozero import Button
from signal import pause  # <- This keeps the script running
import time
import threading
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
            return cls._instance
        
    def __init__(self):
        if self._initialized:
            return  # Already initialized, skip re-initialization

        self._wind_speed_sensor.when_pressed = self.spin()
        self.sample_wind_speed()
        self._initialized = True  # Mark as initialized 

    def sample_wind_speed(self):
        try:
            while True:
                time.sleep(self._sample_rate)
                triggers_per_second = self._wind_count / self._sample_rate
                self.curent_wind_speed = triggers_per_second * self._mph_per_switch
                self._wind_count = 0
                print(f"Current wind speed is {self.curent_wind_speed}")
        except KeyboardInterrupt:
            print("Exiting gracefully")

    
    def spin(self):
        self._wind_count += 1
        print("spin " + str(self._wind_count))