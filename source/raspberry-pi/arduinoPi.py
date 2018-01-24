#!/usr/bin/python
# coding=utf-8

import serial as s
import numpy as np
import datetime

HEADER_FLAG     = 0xA0 # 0b10100000
CONTROL_MASK    = 0xF0 # 0b11110000
SIZE_MASK       = 0x0F # 0b00001111

TEMPERATURE     = 0x00 # 0b00000000
HUMIDITY        = 0x01 # 0b00000001
CO2             = 0x02 # 0b00000010
FAN_INT         = 0x03 # 0b00000011
FAN_EXT         = 0x04 # 0b00000100
SERVOS          = 0x05 # 0b00000101
LED             = 0x06 # 0b00000110
CO2_EXT         = 0x07 # 0b00000111
CO2_CALIBRATE   = 0x08 # 0b00001000
CO2_WARMUP      = 0x09 # 0b00001001

SENSORS_UNAVAILABLE = 0xEE

DAMPERS_CLOSED  = 0
DAMPERS_OPEN    = 1

FLOAT_ERROR     = -1
BAD_VALUE       = -200 # Outside the range of all sensors

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
            timeout=20
        )


        self.serial.isOpen()

        self.time_stamp = 0
        self.temperature = 0
        self.humidity = 0
        self.co2_ppm = 0
        self.co2_ext_ppm = 0
        self.dirty_data = True


        # TODO: try single point calibtration, and this manual calibration may be unnecessary
        # Error margins derived from measurements with a handheld CO2 sensor (Testo 535)
        # self.internal_co2_error_correction = -145   # (between -140 and -130 @ 430-450 ppm)
        # self.external_co2_error_correction = 55     # (between 45 - 65 @ 470-480 ppm)


        self.error = ''

    def command(self, t, v):
        '''
            Sends an instruction to change an actuator/LED via the Arduino
            followed by which value to set.

            v should be a list of bytes, larger values must be split into byte sized elements
        '''
        com = self.make_command(t, v)
        print "sending command:", [hex(b) for b in com]
        self.flush_rcv_buf()
        self.serial.write(com)
        ack = t
        err = t ^ 0xFF

        response = self.receive_uint8()
        if (response == ack):
            print "ACK received from Arduino"
        elif (response == err):
            self.handle_error(response)
        else:
            print "invalid ACK! mismatching response and ack", hex(response), hex(ack)

    def flush_rcv_buf(self):
        self.serial.reset_input_buffer() # Flush input buffer, discarding all its contents

    def corrupt(self,):
        if self.co2_ppm == BAD_VALUE:
            return True
        if self.co2_ext_ppm == BAD_VALUE:
            return True
        if self.humidity == BAD_VALUE:
            return True
        if self.temperature == BAD_VALUE:
            return True

        return False

    def request(self, t, retries=3):
        '''
            Makes a request for parameter (t) to the Arduino and waits for the response.
            Will retry (3 times) if it receives a valid error from the Arduino
        '''
        if retries <= 0:
            return

        req = self.make_request(t)
        print "sending request:", [hex(b) for b in req]
        self.flush_rcv_buf() # Flush receive buffer, in case there has been a desynch
        self.serial.write(req)
        response = self.receive_uint8() # Get the ack or error

        ack = t
        err = t ^ 0xFF

        if response == ack:
            value = self.receive_float()

            if value == FLOAT_ERROR:
                self.flush_rcv_buf() # Flush buffer in case there is a synchronization error
                self.request(t, retries-1)
                return
            print t, value

        elif response == err:
            self.handle_error(response)
            value = BAD_VALUE
        else:
            self.error = 'response neither ACK, nor ERROR (', t, '+ ',response,')'
            return

        self.set_value(t, value)

    def set_value(self, t, val):
        if t == CO2:
            self.co2_ppm = val #+ self.internal_co2_error_correction
        elif t == HUMIDITY:
            self.humidity = val
        elif t == TEMPERATURE:
            self.temperature = val
        elif t == CO2_EXT:
            self.co2_ext_ppm = val #+ self.external_co2_error_correction

    def update(self, types=[TEMPERATURE, HUMIDITY, CO2, CO2_EXT]):
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

        size = len(v) + 2; # +2 for instruction and checksum bytes
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

    def handle_error(self, error):
        error_code = self.receive_uint8()
        print "error", hex(error)
        print "code:", hex(error_code)


    def receive_float(self):
        '''
            Expects to receive 4 bytes from the arduino.
        '''
        allowed_chars = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']

        rsp = self.serial.readline()

        rsp = filter(lambda char: char in allowed_chars, rsp) # Sanitize input to avoid noise

        # May still receive frankenstein input, so catch the exception
        try:
            rsp = float(rsp)
        except ValueError:
            rsp = FLOAT_ERROR

        return rsp

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
        err = t ^ 0xFF

        if response == ack:
            return self.receive_float()
        elif response == err:
            self.handle_error(response)
            time.sleep(0.2)
            read_val(t, retries-1)
        else:
            return -1
