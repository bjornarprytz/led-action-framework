import serial as s
import numpy as np
import datetime

# Communication between the RPi and Arduino are done in packets of 1 byte:
# The first bit indicates whether the following 7 bits are an instruction
# or data following an instruction

FLAG_MASK       = 0x80 # 0b10000000
VALUE_MASK      = 0x7F # 0b01111111

INSTRUCTION     = 0x80 # 0b10000000
VALUE           = 0x00 # 0b00000000

TEMPERATURE     = 0x00 # 0b00000000
HUMIDITY        = 0x01 # 0b00000001
CO2             = 0x02 # 0b00000010
FAN_SPEED       = 0x03 # 0b00000011
SERVOS          = 0x04 # 0b00000100
LED_RED         = 0x05 # 0b00000101
LED_WHT         = 0x06 # 0b00000110
LED_BLU         = 0x07 # 0b00000111

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

    def command(self, f, v):
        '''
            Sends an instruction to change an actuator/LED via the Arduino
            followed by which value to set.
        '''
        packet = self.make_packet(INSTRUCTION, f)
        self.serial.write(packet)
        payload = self.make_packet(VALUE, v)
        self.serial.write(payload)
        ack = self.receive_uint8()
        if (ack == packet):
            print "ACK received from Arduino"
        else:
            print "invalid ACK! mismatching packet and ack", hex(packet), hex(ack)


    def request(self, t, retries=3):
        '''
            Makes a request for parameter (t) to the Arduino and waits for the response.
            Will retry (3 times) if it receives a valid error from the Arduino
        '''
        if retries <= 0:
            return

        packet = self.make_packet(INSTRUCTION, t)
        self.serial.write(packet)
        response = self.receive_uint8()

        ack = t
        err = t & VALUE_MASK

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

    def make_packet(self, f, v):
        '''
            Communication with the arduino is done in 1 byte packets.
            The first bit is used to indicate instruction or data (f).

            (v) is used to specify the type/value of instruction/data.

            Packet:
            1 byte: fvvvvvvv
        '''
        f &= FLAG_MASK  # Mask out the 8th (most significant) bit.
        v &= VALUE_MASK # Clamp the value to 0-127
        packet = np.array ([f | v], dtype=np.uint8)

        return packet

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
