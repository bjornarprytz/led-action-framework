import time
import serial
import numpy as np

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=19200,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)

ser.isOpen()

input=1

addresses = list()

a = 0x00

# Exclude special-use addresses
 # 0000000 0	 General Call
 # 0000000 1	 Start Byte
 # 0000001 X	 CBUS Addresses
 # 0000010 X	 Reserved for Different Bus Formats
 # 0000011 X	 Reserved for future purposes
 # 00001XX X	 High-Speed Master Code
 # 11110XX X	 10-bit Slave Addressing
 # 11111XX X	 Reserved for future purposes

forbidden = [0b00000000, 0b00000001, 0b00000010, 0b00000011,
0b00000100, 0b00000101, 0b00000110, 0b00000111,
0b00001000, 0b00001001, 0b00001010, 0b00001011, 0b00001100, 0b00001101, 0b00001110, 0b00001111,
0b11110000, 0b11110001, 0b11110010, 0b11110011, 0b11110100, 0b11110101, 0b11110110, 0b11110111,
0b11111000, 0b11111001, 0b11111010, 0b11111011, 0b11111100, 0b11111101, 0b11111110, 0b11111111]


for i in range (128):
    if a not in forbidden:
        addresses.append(a)
    a = a + 0x02

# for g in addresses:
#     print hex(g)
#
# print len(addresses)

for ad in addresses:
    rw = 0
    # 1. start sequence
    # 2. i2c-address of slave (write request rw=0)
    # 3. address of internal register
    # 4. start sequence (again)
    # 5. i2c-address of slave (read request: rw=1)
    # 6. read data byte from device
    # 7. stop sequence

    ser.write(start_seq)
    ser.write(ad+rw)
    ser.write(internal_register_address)
    ser.write(start_seq)
    rw = 1
    ser.write(ad+rw)
    out = ''
    # let's wait one second before reading output (let's give device time to answer)
    time.sleep(1)
    while ser.inWaiting() > 0:
        out += ser.read(1)
    ser.write(stop_seq)

    if out != '':
        print out
