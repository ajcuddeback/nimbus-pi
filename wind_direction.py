from gpiozero import MCP3008
import time
import math
import threading
import os
from dotenv import load_dotenv
from logger import Logger

load_dotenv()
logger_instance = Logger(location=os.getenv('STATION_NAME'))

class WindDirection:
    _instance = None
    _lock = threading.Lock()
    _adc = MCP3008(channel=0)
    _volts = {
        0.4: 0.0,
        1.4: 22.5,
        1.2: 45.0, 
        2.8: 67.5, 
        2.7: 90.0, 
        2.9: 112.5,
        2.2: 135.0,
        2.5: 157.5,
        1.8: 180.0,
        2.0: 202.5,
        0.7: 225.0,
        0.8: 247.5,
        0.1: 270.0,
        0.3: 292.5,
        0.2: 315.0,
        0.6: 337.5
    }
    direction = ""

    def __new__(cls, *args, **kwargs):
        with cls._lock:  # Thread-safe singleton
            if cls._instance is None:
                cls._instance = super(WindDirection, cls).__new__(cls)
                cls._instance._initialized = False
                cls._instance.running = False
            return cls._instance
        
    def __init__(self):
        if not getattr(self, '_initialized', False):
            super().__init__()
            self.running = False
            self._initialized = True

    def run(self):
        self.running = True
        try:
            while self.running:
                wind_angle = self.get_value()
                self.direction = wind_angle
                # logger_instance.log.info("Singleton weather direction running")
        except Exception as e:
            logger_instance.log.error(f"WindDirection thread error: {e}")
        finally:
            logger_instance.log.info("WindDirection thread exiting cleanly")

    def stop(self):
        logger_instance.log.warning("Shutting wind direction thread down")
        self.running = False        

    def get_average(self, angles):
        sin_sum = 0.0
        cos_sum = 0.0

        for angle in angles:
            r = math.radians(angle)
            sin_sum += math.sin(r)
            cos_sum += math.cos(r)

        flen = float(len(angles))
        s = sin_sum / flen
        c = cos_sum / flen
        arc = math.degrees(math.atan(s / c))
        average = 0.0

        if s > 0 and c > 0:
            average = arc
        elif c < 0:
            average = arc + 180
        elif s < 0 and c > 0:
            average = arc + 360

        return 0.0 if average == 360 else average    

    def get_value(self, length=5):
        data = []
        # logger_instance.log.info("Measuring wind direction for 5 seconds")
        start_time = time.time()

        while time.time() - start_time <= length:
            if not self.running:
                logger_instance.log.warn("WindDirection measurement interrupted by shutdown.")
                break
            wind = round(self._adc.value*3.3,1)
            if wind not in self._volts:
                logger_instance.log.debug('unknown value' + str(wind))
            else:
                data.append(self._volts[wind])  

        return self.get_average(data)          

    def convert_angle_to_direction(self, angle):
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

        angle = angle % 360
        # Divide full circle into 8 slices of 45°
        index = int((angle + 22.5) // 45) % 8
        return directions[index]