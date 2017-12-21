#!/bin/python
from RPicontrol import *

def is_daytime():
    hour = datetime.datetime.now().hour
    if 6 < hour and hour < 22:
        return True
    else:
        return False

def is_nighttime():
    return not is_daytime()

if __name__ == "__main__":
    handler = PlantEnvironmentControl()

    sun_up = False
    sun_down = True

    t=True

    while True:
        if t:
            print "tick"
        else:
            print "tock"
        t = not t

        if sun_down and is_daytime():
            handler.sunrise([0,0,0], [64, 64, 64], 60)
            sun_up = True
            sun_down = False

        if sun_up and is_nighttime():
            handler.sunset([64, 64, 64], [0,0,0], 60)
            sun_up = False
            sun_down = True

        time.sleep(5)
