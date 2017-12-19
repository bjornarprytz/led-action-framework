#!/bin/python
import time
import database
import sys
from arduinoPi import * # imports datetime


class PlantEnvironmentControl:
    def __init__(self, db_name='plantdb', arduino_port='/dev/ttyACM0'):
        '''
            Initialise the Arduino interface, and connect to a database to store
            the readings.
        '''
        self.arduino = Arduino(arduino_port)
        self.db = database.db(db_name)
        self.db.init_db()
        self.db_up_to_date = False

    def run_experiment(self, title, description, interval_length, num_intervals, normalization_time):
        '''
            Run a full experiment cycle with a set number of intervals
        '''
        start_time = datetime.datetime.now()

        experiment_id = self.db.new_experiment(title, start_time, interval_length, description)

        for i in range(num_intervals):
            self.normalize(air_out_time=normalization_time)

            # TODO: Insert ML search for new input vector
            red = np.random.randint(0x100)
            white = np.random.randint(0x100)
            blue = np.random.randint(0x100)

            self.run_interval(experiment_id, red, white, blue, interval_length)
            self.shut_down()

    def shut_down(self):
        '''
            Shut down all internal devices
        '''

        self.arduino.command(SERVOS, [DAMPERS_CLOSED])
        self.arduino.command(FAN_EXT, [0x00])
        self.arduino.command(FAN_INT, [0x00])
        self.arduino.command(LED, [0,0,0])

    def normalize(self, air_out_time=20, delta_co2_threshold_ppm=10):
        '''
            Open chamber and normalize the internal air by turning up fans

            Measure CO2 periodically to determine when air
            is normalized (change in CO2 is sufficiently small)

            Turn off External fans and close dampers
            Set internal fans to circulate air calmly
        '''

        print 'Normalizing test environments'
        # OPEN DAMPERS AND MAX ALL FANS
        print 'Open dampers and max all fans'
        self.arduino.command(SERVOS, [DAMPERS_OPEN])
        self.arduino.command(FAN_EXT, [0xFF])
        self.arduino.command(FAN_INT, [0xFF])

        # TAKE MEASUREMENT OF CARBON DIOXIDE
        print 'MEASURE CO2'
        prev_co2 = self.arduino.read_val(CO2)

        # WAIT FOR AIRFRLOW TO GET GOING
        print 'Letting air flow for', air_out_time, 'seconds'
        time.sleep(air_out_time)

        # KEEP AIRING OUT CHAMBER UNTIL DELTA CO2 IS LOW ENOUGH
        new_co2 = self.arduino.read_val(CO2)
        delta_co2 = prev_co2 - new_co2
        print 'delta CO2:', delta_co2
        while delta_co2 > delta_co2_threshold_ppm:
            prev_co2 = new_co2
            time.sleep(5)
            new_co2 = self.arduino.read_val(CO2)
            delta_co2 = prev_co2 - new_co2
            print 'delta CO2:', delta_co2

        if prev_co2 == -1 or new_co2 == -1:
            print 'Warning: Arduino communication has broken down', new_co2, prev_co2

        # ADJUST BACK TO NORMAL PROCEDURE
        self.arduino.command(FAN_EXT, [0x00])
        self.arduino.command(FAN_INT, [0x80])
        self.arduino.command(SERVOS, [DAMPERS_CLOSED])

        print "normalization complete at delta_co2:", delta_co2

        return

    def run_interval(self, experiment_id, red, white, blue, length):
        '''
            Intervals Phases:
                1: Adjust LED channels, measure CO2
                2: Wait and do readings while Photosynthesis does work
                3: measure CO2 again
        '''
        print 'experiment ID:', experiment_id
        print 'red:', red
        print 'white:', white
        print 'blue:', blue
        print 'length:', length

        interval_id = self.db.new_interval([red, white, blue, experiment_id])

        # Take measurements from Arduino and log it in the database
        self.update()
        self.log(interval_id)
        # Adjust LED to new settings
        self.arduino.command(LED, [red, white, blue])
        # Wait for a while and take readings
        self.wait_and_read(interval_id, length)
        #
        self.update()
        self.log(interval_id)

    def seconds_passed_since(self, start):
        return (datetime.datetime.now() - start).seconds

    def wait_and_read(self, interval_id, length):
        '''
            Wait for the input length (seconds) of time and do periodic readings
        '''
        start = datetime.datetime.now()

        while self.seconds_passed_since(start) < length:
            self.update()
            self.log(interval_id)
            time.sleep(2)


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
            speed_int = int(raw_input("Internal FAN Speed (0-255)"))
            speed_ext = int(raw_input("External FAN Speed (0-255)"))

            speed_int = self.clamp(speed_int, 0, 255) # Clamp Speed and compress it slightly (right shift 1)
            speed_ext = self.clamp(speed_ext, 0, 255)

            self.arduino.command(FAN_INT, [speed_int])
            self.arduino.command(FAN_EXT, [speed_ext])
        if control == "3":
            self.arduino.command(SERVOS, [DAMPERS_CLOSED])
        if control == "4":
            self.arduino.command(SERVOS, [DAMPERS_OPEN])
        if control == "5":
            red = int(raw_input("red: (0-255)"))
            red = self.clamp(red, 0, 255)
            white = int(raw_input("white: (0-255)"))
            white = self.clamp(white, 0, 255)
            blue = int(raw_input("blue: (0-255)"))
            blue = self.clamp(blue, 0, 255)
            self.arduino.command(LED, [red, white, blue])

    def clamp(self, val, mn, mx):
        return max(mn, min(val, mx))

def parse_args():
    if len(sys.argv) < 5:
        print "Usage: python", sys.argv[0], "title interval_length num_intervals normalization_time [description]"
        exit()

    title = sys.argv[1]
    interval_length = int(sys.argv[2])
    num_intervals = int(sys.argv[3])
    normalization_time = int(sys.argv[4])

    if len(sys.argv) == 6:
        description = sys.argv[5]
    else:
        description = ''

    return title, description, interval_length, num_intervals, normalization_time

if __name__ == "__main__":
    handler = PlantEnvironmentControl()
    print "Grace period for Arduino"
    grace = 3
    for _ in range(grace):
        time.sleep(1)
        print '.'

    if len(sys.argv) == 1:
        while True:
            key = raw_input(">>>")

            handler.control(key)

    title, description, interval_length, num_intervals, normalization_time = parse_args()

    handler.run_experiment(title, description, interval_length, num_intervals, normalization_time)

    handler.db.print_experiment(title)
