'''
 # @file DFRobot_AS3935_ordinary.py
 # @brief SEN0290 Lightning Sensor
 # @n This sensor can detect lightning and display the distance and intensity of the lightning within 40 km
 # @n It can be set as indoor or outdoor mode.
 # @n The module has three I2C, these addresses are:
 # @n  AS3935_ADD1  0x01   A0 = 1  A1 = 0
 # @n  AS3935_ADD2  0x02   A0 = 0  A1 = 1
 # @n  AS3935_ADD3  0x03   A0 = 1  A1 = 1
 # @copyright   Copyright (c) 2010 DFRobot Co.Ltd (http://www.dfrobot.com)
 # @licence     The MIT License (MIT)
 # @author [TangJie](jie.tang@dfrobot.com)
 # @version  V1.0.2
 # @date  2019-09-28
 # @url https://github.com/DFRobor/DFRobot_AS3935
'''

import sys
sys.path.append('../')
import time
from DFRobot_AS3935_Lib import DFRobot_AS3935
import RPi.GPIO as GPIO
from datetime import datetime
from logger import Logger
import os
from mqtt_client import MQTTClient
import threading

logger_instance = Logger(location=os.getenv('STATION_NAME'))
mqtt_client_instance = MQTTClient(host="localhost", port=1883)

#I2C address
AS3935_I2C_ADDR1 = 0X01
AS3935_I2C_ADDR2 = 0X02
AS3935_I2C_ADDR3 = 0X03

#Antenna tuning capcitance (must be integer multiple of 8, 8 - 120 pf)
AS3935_CAPACITANCE = 96
IRQ_PIN = 7

#Indoor/outdoor mode selection
AS3935_INDOORS = 0
AS3935_OUTDOORS = 1
AS3935_MODE = AS3935_INDOORS

#Enable/disable disturber detection
AS3935_DIST_DIS = 0
AS3935_DIST_EN = 1
AS3935_DIST = AS3935_DIST_EN

GPIO.setmode(GPIO.BOARD)

sensor = DFRobot_AS3935(AS3935_I2C_ADDR3, bus = 1)
if (sensor.reset()):
  print("init sensor sucess.")
else:
  print("init sensor fail")
  while True:
    pass

#Configure sensor
sensor.manual_cal(AS3935_CAPACITANCE, AS3935_MODE, AS3935_DIST)

class Lightning:
    _instance = None
    _lock = threading.Lock()
    _station_id = ""

    def __new__(cls, *args, **kwargs):
        with cls._lock:  # Thread-safe singleton
            if cls._instance is None:
                cls._instance = super(Lightning, cls).__new__(cls)
                cls._instance._initialized = False
                cls._instance.running = False
            return cls._instance
        
    def __init__(self, station_id):
        if not getattr(self, '_initialized', False):
            super().__init__()
            self.running = False
            self._initialized = True
            self._station_id = station_id


    def begin_lightning_detection(self):
        

      # Connect the IRQ and GND pin to the oscilloscope.
      # uncomment the following sentences to fine tune the antenna for better performance.
      # This will dispaly the antenna's resonance frequency/16 on IRQ pin (The resonance frequency will be divided by 16 on this pin)
      # Tuning AS3935_CAPACITANCE to make the frequency within 500/16 kHz plus 3.5% to 500/16 kHz minus 3.5%
      #
      # sensor.setLco_fdiv(0)
      # sensor.set_irq_output_source(3)

      #view all register data
      #sensor.print_all_regs()
      #Set to input mode
      GPIO.setup(IRQ_PIN, GPIO.IN)
      #Set the interrupt pin, the interrupt function, rising along the trigger
      GPIO.add_event_detect(IRQ_PIN, GPIO.RISING, callback = self.callback_handle)
      logger_instance.log.info("start lightning detect.")

      while self.running:
        time.sleep(1.0)

    def run(self):
        self.running = True
        self.begin_lightning_detection()
       
    def stop(self):
        logger_instance.log.info("Shutting lightning thread down")
        self.running = False

    def callback_handle(self, channel):
      global sensor
      time.sleep(0.005)
      intSrc = sensor.get_interrupt_src()
      if intSrc == 1:
        lightning_distKm = sensor.get_lightning_distKm()
        logger_instance.log.info('Lightning occurs!')
        logger_instance.log.info('Distance: %dkm'%lightning_distKm)

        lightning_energy_val = sensor.get_strike_energy_raw()
        logger_instance.log.info('Intensity: %d '%lightning_energy_val)


        data = {
          "distance": lightning_distKm,
          "distanceFormat": "km",
          "intensity": lightning_energy_val,
          "stationId": self.station_id,
          "timestamp": round(time.time())
        }
        
        logger_instance.log.info(data)
        mqtt_client_instance.publish("weather/lightning", data)

      elif intSrc == 2:
        logger_instance.log.info('Disturber discovered!')
      elif intSrc == 3:
        logger_instance.log.info('Noise level too high!')      