#!/bin/python
import time
import database
from arduinoPi import * # imports datetime

db_name = 'plantdb'

class PlantEnvironmentControl:
    def __init__(self, arduino_port='/dev/ttyACM0'):
        '''
            Initialise the Arduino interface, and connect to a database to store
            the readings.
        '''
        self.arduino = Arduino(arduino_port)
        self.db = database.db(db_name)
        self.db.init_db()
        self.db_up_to_date = False

    def log(self, interval_id):
        '''
            The readings are catalogued by interval id. This function inserts
            the latest reading from the Arduino into the database
        '''
        if self.db_up_to_date:
            print "database already has this reading logged"
            return

        print self.arduino.time_stamp, self.arduino.temperature, self.arduino.humidity, self.arduino.co2_ppm    
        self.db.insert_readings((self.arduino.time_stamp, self.arduino.temperature, self.arduino.humidity, self.arduino.co2_ppm, interval_id))

        self.db_up_to_date = True

    def update(self):
        '''
            Requests a status  update from the Arduino.
        '''

        self.arduino.update()
        self.db_up_to_date = False

    def control(self, control):
        '''
            This code is only used for unit testing. At the bottom of this file,
            there's code that listens for user input to and sends it here.
        '''
        if control == "0":
            self.log("test experiment")
        if control == "1":
            self.update()
        if control == "2":
            speed = int(raw_input("Internal FAN Speed (0-255)"))
            speed = self.clamp(speed, 0, 255) # Clamp Speed and compress it slightly (right shift 1)
            self.arduino.command(FAN_SPEED, [speed])
        if control == "3":
            self.arduino.command(SERVOS, [DAMPERS_CLOSED])
        if control == "4":
            self.arduino.command(SERVOS, [DAMPERS_OPEN])
        if control == "5":
            red = int(raw_input("red: (0-255)"))
            red = self.clamp(red, 0, 255)
            white = int(raw_input("white: (0-255)"))
            white = self.clamp(white, 0, 255)
            blue = int(raw_input("blue: (0-255)")) % 0x100
            blue = self.clamp(blue, 0, 255)
            self.arduino.command(LED, [red, white, blue])

    def clamp(self, val, mn, mx):
        return max(mn, min(val, mx))

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
