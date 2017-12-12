import serial as s
import numpy as np
import datetime

# Communication between the RPi and Arduino are done in packets of 1 byte:
# The first bit indicates whether the following 7 bits are an instruction
# or data following an instruction

CONTROL_MASK    = 0b11110000
HANDSHAKE_FLAG  = 0b10100000
SIZE_MASK       = 0x0F # 0b00001111

TEMPERATURE     = 0x00 # 0b00000000
HUMIDITY        = 0x01 # 0b00000001
CO2             = 0x02 # 0b00000010
FAN_SPEED       = 0x03 # 0b00000011
SERVOS          = 0x04 # 0b00000100
LED             = 0x05 # 0b00000101

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
        print v
        com = self.make_command(t, v)
        print "sending command:", com
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
        print "sending request:", req
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
            request(t, retries-1)
        else:
            self.error = 'response neither ACK, nor ERROR ('+t+', '+response+')'

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

            (c) is used to indicate a header byte (1111xxxx)
            (s) is used to specify the size of the payload.
            (t) is the instruction
            (v) value can be anything, and has to be specified by the Arduino Code
        '''

        size = len(v) + 1;
        if size > 0x0F:
            print "invalid size:", size
            return




        header = np.array ([HANDSHAKE_FLAG | size], dtype=np.uint8)
        payload = np.array ([t] + v, dtype=np.uint8)

        return np.concatenate((header, payload))

    def make_request(self, t):
        '''
        Request:
            Header:     ccccssss
            Payload:    tttttttt

            (c) is used to indicate a header byte (1111xxxx)
            (s) is used to specify the size of the payload.
            (t) is the instruction and specifies what is being requested
        '''

        size = 0x01; # Requests only contain the instruction type (size: 1 byte)

        header = np.array ([HANDSHAKE_FLAG | size], dtype=np.uint8)
        payload = np.array ([t], dtype=np.uint8)

        return np.concatenate((header, payload))

    def receive_float(self):
        '''
            Expects to receive 4 bytes from the arduino.
        '''
        rsp = float(self.serial.readline())
        return rsp

    def receive_uint8(self):
        '''
            Receive 1 byte from the arduino.
        '''
        rsp = np.uint8(ord(self.serial.read()))
        return rsp
