import matplotlib.pyplot as plt
import serial as s
import time as t
import numpy as np
import sys

# Read co2 levels at certain intervals, over a time period (input)
# Output a pyplot graph of the change during the input period.

# This program is made for the T6613 co2 sensor
# by Bjornar Prytz


# Commands sent to the sensor have the following format:
# <flag> <address> <length> <command> <additional_data>*
# where each <> constitutes 1 byte. *can span multiple bytes



# Responses from the sensor has the following format:

# <flag> <address> <length> <response_data>


# <flag> = 0xFF
# <address> = 0xFE (general to all sensors) TODO: Make this specific
# <length> = the count of bytes in the rest of the message
# <command> = the function
# <additional_data> = the parameter(s)


# Masks for status check
ERROR = 0b00000001 # error
WRMUP = 0b00000010 # warmup mode
CLBRT = 0b00000100 # calibration
IDLMD = 0b00001000 # idle mode
STEST = 0b10000000 # self test mode



def convert_gas_ppm(buf):
    # From the data sheet of the T6613 co2 sensor:
    # Response is a 2-byte binary value giving the PPM. For some models,
    # the PPM value is an unsigned integer between 0 and 65,535. For
    # other models, it is a signed value between -32768 and 32767.
    # Order of the returned bytes is <msb,lsb>. For some sensor models,
    # this value must be multiplied by 16 to obtain the actual PPM.
    if buf.size <= 0:
        return 0

    msb = buf[0]
    lsb = buf[1]

    return (msb << 8) + lsb

def read_response(serial, full=False):

    hdr_len = 3 # flag, address and length should always be present
    header = np.frombuffer(serial.read(hdr_len), dtype=np.uint8)

    if header.size < hdr_len:
        return np.array([-1])

    # print "address: ", hex(header[1])

    # print "header: ", header

    pl_len = header[-1] # Find out how many bytes the payload is
    if pl_len > 0:
        payload = np.frombuffer(serial.read(pl_len), dtype=np.uint8)

    else:
        # payload = np.ndarray([0], dtype=np.uint8)
        return np.array([-1])


    # print "payload: ", payload

    if full:
        response = np.concatenate((header, payload))
        return response
    else:
        return payload

def cmd_read_gas_ppm(serial):

    retries = 2 # amount of retries before giving up

    flag = 0xFF
    adr = 0xFE

    len = 0x02
    cmd = 0x02
    prm = 0x03 # additional_data

    msg=np.array([flag, adr, len, cmd, prm], dtype=np.uint8)

    while retries:
        serial.write(msg)
        rsp = read_response(serial)
        print rsp
        if rsp[0] == -1:
            print "bad, or no response: retrying"
            retries -= 1
        else:
            break

    return rsp

def cmd_warmup(serial):
    # Reset the sensor (wait a while before reading from it)

    flag = 0xFF
    adr = 0xFE

    len = 0x01
    cmd = 0x84

    msg=np.array([flag, adr, len, cmd], dtype=np.uint8)

    serial.write(msg)
    read_response(serial)

def cmd_status(serial, status):
    # returns True if the sensor is in the input status

    return cmd_get_status(serial) & status

def cmd_get_status(serial):

    flag = 0xFF
    adr = 0xFE

    len = 0x01
    cmd = 0xB6

    msg=np.array([flag, adr, len, cmd], dtype=np.uint8)
    serial.write(msg)

    rsp = read_response(serial)
    status = rsp[0]

    return status

def print_status(serial):
    status = cmd_get_status(serial)

    if status & ERROR:
        print "error"
    if status & WRMUP:
        print "warmup"
    if status & CLBRT:
        print "calibration"
    if status & IDLMD:
        print "idle mode"
    if status & STEST:
        print "self test"

if __name__ == "__main__":
    ser = s.Serial(
        port='/dev/ttyUSB0',
        baudrate=19200,
        parity=s.PARITY_NONE,
        stopbits=s.STOPBITS_ONE,
        bytesize=s.EIGHTBITS,
        timeout=2
    )

    ser.isOpen()

    print "Warming up.."
    cmd_warmup(ser)
    t.sleep(1)
    while cmd_status(ser, WRMUP):
        print "."
        t.sleep(1)

    print "Warmup complete!"

    for i in range(0, 150, 5):
        res = cmd_read_gas_ppm(ser)
        ppm = convert_gas_ppm(res)
        plt.plot(i, ppm, color="red", marker="*", markersize=9)
        print ppm
        t.sleep(5)

    plt.ylabel('ppm')
    plt.xlabel('time(s)')
    plt.show()
