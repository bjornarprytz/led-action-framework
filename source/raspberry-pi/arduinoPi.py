#!/usr/bin/python
# coding=utf-8

import serial as s
import numpy as np
import datetime

CONTROL_MASK    = 0b11110000
HEADER_FLAG     = 0b10100000 # 0xA0
SIZE_MASK       = 0x0F # 0b00001111

TEMPERATURE     = 0x00 # 0b00000000
HUMIDITY        = 0x01 # 0b00000001
CO2             = 0x02 # 0b00000010
FAN_INT         = 0x03 # 0b00000011
FAN_EXT         = 0x04 # 0b00000100
SERVOS          = 0x05 # 0b00000101
LED             = 0x06 # 0b00000110

DAMPERS_CLOSED  = 0
DAMPERS_OPEN    = 1

class Arduino:
    def __init__(self, serial_port):
        '''
            Initialise an interface with an Arduino.
        '''
        self.serial = s.Serial(
            port=serial_port,
            baudrate=9600,
            parity=s.PARITY_NONE,
            stopbits=s.STOPBITS_ONE,
            bytesize=s.EIGHTBITS,
            timeout=5
        )

        self.serial.isOpen()

        self.time_stamp = 0
        self.temperature = 0
        self.humidity = 0
        self.co2_ppm = 0


        self.error = ''

    def command(self, t, v):
        '''
            Sends an instruction to change an actuator/LED via the Arduino
            followed by which value to set.
        '''
        com = self.make_command(t, v)
        print "sending command:", [hex(b) for b in com]
        self.serial.write(com)
        ack = t
        err = ~t

        response = self.receive_uint8()
        if (response == ack):
            print "ACK received from Arduino"
        else:
            print "invalid ACK! mismatching response and ack", hex(response), hex(ack)


    def request(self, t, retries=3):
        '''
            Makes a request for parameter (t) to the Arduino and waits for the response.
            Will retry (3 times) if it receives a valid error from the Arduino
        '''
        if retries <= 0:
            return

        req = self.make_request(t)
        print "sending request:", [hex(b) for b in req]
        self.serial.write(req)
        response = self.receive_uint8()

        ack = t
        err = ~t

        if response == ack:
            value = self.receive_float()

            if t == CO2:
                self.co2_ppm = value
            elif t == HUMIDITY:
                self.humidity = value
            elif t == TEMPERATURE:
                self.temperature = value
        elif response == err:
            time.sleep(0.2)
            request(t, retries-1)
        else:
            self.error = 'response neither ACK, nor ERROR (', t, '+ ',response,')'

    def update(self, types=[TEMPERATURE, HUMIDITY, CO2]):
        '''
            Request [all] (types) of parameters from the Arduino. These are stored
            in-memory on-board the Arduino. Mark the reading with a timestamp.
        '''
        for t in types:
            self.request(t)
        self.time_stamp = datetime.datetime.now()

    def make_command(self, t, v):
        '''
        Command:
            Header:     ccccssss
            Payload:    tttttttt, vvvvvvvv, ...
            Checksum:   xxxxxxxx

            (c) is used to indicate a header byte (1111xxxx)
            (s) is used to specify the size of the payload.
            (t) is the instruction
            (v) value can be anything, and has to be specified in the Arduino Code
            (x) is a function of the payload
        '''

        size = len(v) + 2; # +2 for instruction and checksum
        if size > 0x0F:
            print "invalid size:", size
            return

        type_b = np.array([t], dtype=np.uint8)
        value_b = np.array(v, dtype=np.uint8)

        header = np.array ([HEADER_FLAG | size], dtype=np.uint8)
        payload = np.concatenate((type_b, value_b))
        checksum = np.array([self.get_checksum(payload)], dtype=np.uint8)

        command = np.concatenate((header, payload, checksum))

        return command

    def make_request(self, t):
        '''
        Request:
            Header:     ccccssss
            Payload:    tttttttt
            Checksum:   xxxxxxxx

            (c) is used to indicate a header byte (1111xxxx)
            (s) is used to specify the size of the payload.
            (t) is the instruction and specifies what is being requested
            (x) is a function of the payload
        '''

        size = 0x02; # Requests only contain the instruction type and checksum (size: 1 byte each)

        header = np.array ([HEADER_FLAG | size], dtype=np.uint8)
        payload = np.array ([t], dtype=np.uint8)
        checksum = np.array([self.get_checksum(payload)], dtype=np.uint8)

        request = np.concatenate((header, payload, checksum))

        return request

    def get_checksum(self, payload):
        cs = 0
        for byte in payload:
            cs += byte
        cs %= 0x100
        return cs

    def receive_float(self):
        '''
            Expects to receive 4 bytes from the arduino.
        '''
        allowed = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']

        rsp = self.serial.readline()

        rsp = filter(lambda char: char in allowed, rsp) # Sanitize input to avoid noise

        return float(rsp)

    def receive_uint8(self):
        '''
            Receive 1 byte from the arduino.
        '''

        rsp = np.uint8(ord(self.serial.read()))
        return rsp

    def read_val(self, t, retries=5):
        if retries <= 0:
            return -1

        req = self.make_request(t)
        self.serial.write(req)
        response = self.receive_uint8()

        ack = t
        err = ~t

        if response == ack:
            return self.receive_float()
        elif response == err:
            time.sleep(0.2)
            read_val(t, retries-1)
        else:
            return -1
