from gpiozero import Button
from signal import pause  # <- This keeps the script running
import time

wind_speed_sensor = Button(5)
wind_count = 0
curent_wind_speed = 0
mph_per_switch = 1.492
sample_rate = 5

def spin():
    global wind_count
    wind_count += 1
    print("spin " + str(wind_count))

wind_speed_sensor.when_pressed = spin

try:
    while True:
        time.sleep(sample_rate)
        triggers_per_second = wind_count / sample_rate
        curent_wind_speed = triggers_per_second * mph_per_switch
        print(f"Current wind speed is {curent_wind_speed}")
except KeyboardInterrupt:
    print("Exiting gracefully")



pause()