#!/bin/python
import time
import datetime
import serial as s
import numpy as np

import os.path
import glob
import plot
import database

db_name = 'plantdb'

# Communication between the RPi and Arduino are done in packets of 1 byte:
# The first bit indicates whether the following 7 bits are an instruction
# or data following an instruction

TYPE_MASK    = 0x80 # 0b10000000
VALUE_MASK   = 0x7F # 0b01111111

INSTRUCTION  = 0x80 # 0b10000000
VALUE        = 0x00 # 0b00000000

TEMPERATURE  = 0x00 # 0b00000000
HUMIDITY     = 0x01 # 0b00000001
CO2          = 0x02 # 0b00000010
FAN_SPEED    = 0x03 # 0b00000011
SERVOS       = 0x04 # 0b00000100
LED_RED      = 0x05 # 0b00000101
LED_WHT      = 0x06 # 0b00000110
LED_BLU      = 0x07 # 0b00000111

RSP_TMP     = 0x0 # 0b0000
RSP_HUM     = 0x4 # 0b0100
RSP_CO2     = 0x8 # 0b1000

class PlantEnvironmentControl:
    def __init__(self, serial_port='/dev/ttyACM0'):

        self.arduino = s.Serial(
            port=serial_port,
            baudrate=9600,
            parity=s.PARITY_NONE,
            stopbits=s.STOPBITS_ONE,
            bytesize=s.EIGHTBITS,
            timeout=2
        )
        self.arduino.isOpen()

        self.temperature = 0
        self.humidity = 0
        self.co2_ppm = 0

        self.db = database.db(db_name)
        self.db.init_db()

    def handle(self, response):
        # print "handling"
        rsp_type = response >> 4 # Isolate the type bits of the response

        if rsp_type == RSP_TMP:
            # print "update temperature"
            self.temperature = self.receive_float()
        if rsp_type == RSP_HUM:
            # print "update humidity"
            self.humidity = self.receive_float()
        if rsp_type == RSP_CO2:
            # print "update co2 ppm"
            self.co2_ppm = self.receive_float()

    def log(self, experiment_id):

        now = datetime.datetime.now()
        self.db.insert_readings((now, self.temperature, self.humidity, self.co2_ppm, experiment_id))

        # entry = {
        # 'time' : now.strftime("%H:%M"),
        # 'temp' : self.temperature,
        # 'hum' : self.humidity,
        # 'co2' : self.co2_ppm
        # }


    def control(self, control):
        '''
            This code is only used for unit testing. At the bottom of this file,
            there's code that listens for user input to and sends it here.
        '''
        if control == "0":
            self.log("test experiment")
        if control == "1":
            self.update([TEMPERATURE])
        if control == "2":
            self.update([HUMIDITY])
        if control == "3":
            self.update([CO2])
        if control == "4":
            self.command(FAN_SPEED, 0x50)
        if control == "5":
            self.command(SERVOS, 0x10)
        if control == "6":
            self.command(LED_RED, 0x15)
        if control == "7":
            self.command(LED_WHT, 0x58)
        if control == "8":
            self.command(LED_BLU, 0x42)



    def make_packet(self, t, v):
        '''
            Communication with the arduino is done in 1 byte packets.
            The first bit is used to indicate instruction or data (t).

            (v) is used to specify the instruction / data.
        '''
        t &= TYPE_MASK
        v &= VALUE_MASK # Clamp the value to 0-127
        packet = np.array ([t | v], dtype=np.uint8)

        return packet

    def receive_float(self):
        rsp = float(self.arduino.readline())
        return rsp

    def receive_uint8(self):
        '''
            Receive 1 byte from the arduino. A request is required in order
            to receive anything from the Arduino.
        '''
        rsp = np.uint8(ord(self.arduino.read()))
        return rsp

    def send(self, packet):
        self.arduino.write(packet)

    def request(self, t):
        '''

        '''
        packet = self.make_packet(INSTRUCTION, t)
        self.send(packet)

    def update(self, types=[TEMPERATURE, HUMIDITY, CO2]):
        '''
            Request (all) types of parameters from the Arduino. These are stored
            in-memory on-board the Arduino.
        '''
        for t in types:
            self.request(t) #
            response = self.receive_uint8()
            self.handle(response)

    def command(self, t, v):
        '''
            Sends an instruction to change an actuator/LED via the Arduino
            followed by which value to set.
        '''
        packet = self.make_packet(INSTRUCTION, t)
        self.send(packet)
        payload = self.make_packet(VALUE, v)
        self.send(payload)

        # TODO: Wait for ACK from arduino

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
