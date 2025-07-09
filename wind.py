from gpiozero import Button
from signal import pause  # <- This keeps the script running

wind_speed_sensor = Button(5)
wind_count = 0

def spin():
    global wind_count
    wind_count += 1
    print("spin " + str(wind_count))

wind_speed_sensor.when_pressed = spin

pause()