#!/bin/python
import time
import database
import sys
from arduinoPi import * # imports datetime, numpy and serial
import list_ports

FANS_OFF = 0x00
FANS_LOW = 0x40
FANS_HIGH = 0x80
FANS_FULL = 0xFF

class PlantEnvironmentControl:
    def __init__(self, db_name='plantdb', port_list=['/dev/ttyACM0', '/dev/ttyACM1'], grace=3):
        '''
            Initialise the Arduino interface, and connect to a database to store
            the readings.
        '''

        serial_port = self.find_available_port(port_list)

        if serial_port == None:
            print port_list, 'were not available'
            return

        self.arduino = Arduino(serial_port)



        self.db = database.db(db_name)
        self.db.init_db()
        self.db_up_to_date = False

        print "Grace period for Arduino (",grace," seconds)"
        for _ in range(grace):
            time.sleep(1)
            print '.'

    def find_available_port(self, port_list):
        '''
            Look for the ports in the given port_list among the connected serial ports.
        '''
        for available_port in list_ports.serial_ports():
            for port_to_try in port_list:
                if port_to_try == available_port:
                    return available_port
        return None

    def run_experiment(self, title, description, interval_length, num_intervals, normalization_time, seed_setting={'r':0xFF, 'w':0xFF, 'b':0xFF}):
        '''
            Run a full experiment cycle with a set number of intervals
        '''
        start_time = datetime.datetime.now()

        experiment_id = self.db.new_experiment(title, start_time, interval_length, description)

        red = seed_setting['r']
        white = seed_setting['w']
        blue = seed_setting['b']

        for i in range(num_intervals):

            interval_id = self.db.new_interval([red, white, blue, experiment_id])

            self.normalize(interval_id, air_out_time=normalization_time)

            # TODO: Insert search for new input vector

            self.run_interval(interval_id, red, white, blue, interval_length)
            self.shut_down()


    def shut_down(self):
        '''
            Shut down all internal devices
        '''

        self.arduino.command(SERVOS, [DAMPERS_CLOSED])
        self.arduino.command(FAN_EXT, [FANS_OFF])
        self.arduino.command(FAN_INT, [FANS_LOW])
        self.arduino.command(LED, [0,0,0])

    def normalize(self, interval_id, air_out_time=20, delta_co2_threshold_ppm=10):
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
        self.arduino.command(FAN_EXT, [FANS_FULL])
        self.arduino.command(FAN_INT, [FANS_FULL])
        self.arduino.command(LED, [0,0,0])

        # TAKE MEASUREMENT OF CARBON DIOXIDE
        # print 'MEASURE CO2'
        # prev_co2 = self.arduino.read_val(CO2)

        # WAIT FOR AIRFRLOW TO GET GOING
        print 'Letting air flow for', air_out_time, 'seconds'
        self.wait_and_read(interval_id, air_out_time)

        # KEEP AIRING OUT CHAMBER UNTIL DELTA CO2 IS LOW ENOUGH
        # new_co2 = self.arduino.read_val(CO2)
        # delta_co2 = prev_co2 - new_co2
        # print 'delta CO2:', delta_co2
        # while delta_co2 > delta_co2_threshold_ppm:
        #     prev_co2 = new_co2
        #     time.sleep(5)
        #     new_co2 = self.arduino.read_val(CO2)
        #     delta_co2 = prev_co2 - new_co2
        #     print 'delta CO2:', delta_co2
        #
        # if prev_co2 == -1 or new_co2 == -1:
        #     print 'Warning: Arduino communication has broken down', new_co2, prev_co2

        # ADJUST BACK TO NORMAL PROCEDURE
        self.arduino.command(FAN_EXT, [FANS_OFF])
        self.arduino.command(FAN_INT, [FANS_LOW])
        self.arduino.command(SERVOS, [DAMPERS_CLOSED])

        # print "normalization complete at delta_co2:", delta_co2

        return

    def run_interval(self, interval_id, red, white, blue, length):
        '''
            Intervals Phases:
                1: Adjust LED channels, measure CO2
                2: Wait and do readings while Photosynthesis does work
                3: measure CO2 again
        '''
        print 'red:', red
        print 'white:', white
        print 'blue:', blue
        print 'length:', length



        # Take measurements from Arduino and log it in the database
        self.update()
        self.log(interval_id)
        # Adjust LED to new settings
        self.arduino.command(LED, [red, white, blue])
        # Wait for a while and take readings
        self.wait_and_read(interval_id, length) # loop
        # Do one last reading, just to be safe
        self.update()
        self.log(interval_id)

    def seconds_passed_since(self, start):
        return (datetime.datetime.now() - start).seconds

    def wait_and_read(self, interval_id, length, read_frequency=4):
        '''
            Wait for the input length (seconds) of time and do periodic readings in the meantime
        '''
        start = datetime.datetime.now()

        while self.seconds_passed_since(start) < length:
            self.update()
            self.log(interval_id)
            time.sleep(read_frequency)


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
        '''
            clamp return value between (inclusive) mn and mx
        '''
        return max(mn, min(val, mx))

    def sunrise(self, f, t, period):

        from_setting = np.array(f, dtype=np.uint8)
        to_setting = np.array(t, dtype=np.uint8)
        if len(from_setting) != 3 or len(to_setting) != 3:
            print "SUNRISE: from_light and to_light invalid. must be on form [red, white, blue]"
            return

        start = datetime.datetime.now()
        setting = np.array(from_setting, dtype=np.uint8)

        if period < 10:
            period = 10 # At least 10 seconds to avoid division by zero

        change = (to_setting - from_setting) / (period / 10) # find how much the light has to change every 10 seconds

        while (self.seconds_passed_since(start) < period):
            self.arduino.command(LED, setting)
            setting += change
            time.sleep(10)
        self.arduino.command(LED, to_setting)

    def sunset(self, f, t, period):
        from_setting = np.array(f, dtype=np.uint8)
        to_setting = np.array(t, dtype=np.uint8)
        if len(from_setting) != 3 or len(to_setting) != 3:
            print "SUNSET: from_light and to_light invalid. must be on form [red, white, blue]"
            return

        start = datetime.datetime.now()
        setting = np.array(from_setting, dtype=np.uint8)

        if period < 10:
            period = 10 # At least 10 seconds to avoid division by zero

        change = (from_setting - to_setting) / (period / 10) # find how much the light has to change every 10 seconds

        while (self.seconds_passed_since(start) < period):
            self.arduino.command(LED, setting)
            setting -= change
            time.sleep(10)
        self.arduino.command(LED, to_setting)

def __parse_args():
    '''
        private function for running this script
    '''
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
        # Default to description holding normalization_time. This is useful info during data collection
        description = normalization_time

    return title, description, interval_length, num_intervals, normalization_time

if __name__ == "__main__":
    handler = PlantEnvironmentControl()

    if len(sys.argv) == 1:
        while True:
            key = raw_input(">>>")

            handler.control(key)

    title, description, interval_length, num_intervals, normalization_time = __parse_args()

    handler.run_experiment(title, description, interval_length, num_intervals, normalization_time)

    handler.db.print_experiment(title)
