import serial as s
import numpy as np

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

# RSP_TMP     = 0x0 # 0b0000
# RSP_HUM     = 0x4 # 0b0100
# RSP_CO2     = 0x8 # 0b1000


class Arduino:
    def __init__(self, serial_port):

        self.serial = s.Serial(
            port=serial_port,
            baudrate=9600,
            parity=s.PARITY_NONE,
            stopbits=s.STOPBITS_ONE,
            bytesize=s.EIGHTBITS,
            timeout=2
        )

        self.serial.isOpen()

        self.temperature = 0
        self.humidity = 0
        self.co2_ppm = 0

        self.error = ''

    def command(self, t, v):
        '''
            Sends an instruction to change an actuator/LED via the Arduino
            followed by which value to set.
        '''
        packet = self.make_packet(INSTRUCTION, t)
        self.serial.write(packet)
        payload = self.make_packet(VALUE, v)
        self.serial.write(payload)

        # TODO: Wait for ACK from arduino

    def request(self, t):
        '''
            Makes a request for parameter t to the Arduino and waits for the response
        '''

        packet = self.make_packet(INSTRUCTION, t)
        self.serial.write(packet)
        response = self.receive_uint8()

        if t == response:
            value = self.receive_float()

            if t == CO2:
                self.co2_ppm = value
            elif t == HUMIDITY:
                self.humidity = value
            elif t == TEMPERATURE:
                self.temperature = value
        else:
            self.error = 'mismatching type and response ('+t+', '+response+')'

    def update(self, types=[TEMPERATURE, HUMIDITY, CO2]):
        '''
            Request (all) types of parameters from the Arduino. These are stored
            in-memory on-board the Arduino.
        '''
        for t in types:
            self.request(t) #

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
        rsp = float(self.serial.readline())
        return rsp

    def receive_uint8(self):
        '''
            Receive 1 byte from the arduino. A request must be made before the
            the Arduino will send anything back.
        '''
        rsp = np.uint8(ord(self.serial.read()))
        return rsp
