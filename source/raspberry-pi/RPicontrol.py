#!/bin/python
import time
import datetime

import os.path
import glob
import plot
import database
from arduinoPi import *

db_name = 'plantdb'



class PlantEnvironmentControl:
    def __init__(self, arduino_port='/dev/ttyACM0'):

        self.arduino = Arduino(arduino_port)
        self.db = database.db(db_name)
        self.db.init_db()

    def log(self, experiment_id):
        now = datetime.datetime.now()
        self.db.insert_readings((now, self.arduino.temperature, self.arduino.humidity, self.arduino.co2_ppm, experiment_id))

    def update(self):
        self.arduino.update()

    def control(self, control):
        '''
            This code is only used for unit testing. At the bottom of this file,
            there's code that listens for user input to and sends it here.
        '''
        if control == "0":
            self.log("test experiment")
        if control == "1":
            self.arduino.update()
        if control == "2":
            self.arduino.command(FAN_SPEED, 0x50)
        if control == "3":
            self.arduino.command(SERVOS, DAMPERS_CLOSED)
        if control == "4":
            self.arduino.command(SERVOS, DAMPERS_OPEN)
        if control == "6":
            self.arduino.command(LED_RED, 0x15)
        if control == "7":
            self.arduino.command(LED_WHT, 0x58)
        if control == "8":
            self.arduino.command(LED_BLU, 0x42)

if __name__ == "__main__":
    update_interval = 10 # seconds
    log_interval = 60 # seconds
    plot_interval = 10 # minutes
    now = datetime.datetime.now()

    handler = PlantEnvironmentControl()
    handler.db.new_experiment("test experiment", now, '', '')
    while True:
        key = raw_input(">>>")

        handler.control(key)
