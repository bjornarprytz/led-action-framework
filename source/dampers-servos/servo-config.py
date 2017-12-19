import serial as s
import numpy as np
import time

def addChecksumAndLength(buf):
    # adding length
    # print "size: ", buf.size
    buf[3] = (buf.size - 4)


    # finding sum

    checksum = 0
    for i in range(2, buf.size-1):
        tmp = buf[i]
        if (tmp < 0):
            tmp = tmp + 256
        checksum += tmp
    # inverting bits
    checksum = ~checksum
    # int2byte
    checksum = checksum & 255

    # adding checkSum
    buf[-1] = checksum

    # print checksum
    # print buf
    return buf



 # ======================= Writes 0<val<255 to register "regNo" in servo "id" ======================

def setReg1(serial, addr, regNo, val):
    buf = np.array([0xFF, 0xFF, 0, 0, 0x3, 0, 0, 0], dtype=np.uint8)

    buf[2] = addr
    buf[5] = regNo
    buf[6] = val

    buf = addChecksumAndLength(buf)

    # print buf

    serial.write(buf)

 # ======================= Writes 0<val<1023 to register "regNoLSB/regNoLSB+1" in servo "id" =======

def setReg2(serial, addr, regNoLSB, val):
    buf = np.array([0xFF, 0xFF, 0, 0, 0x3, 0, 0, 0, 0], dtype=np.uint8)

    buf[2] = addr
    buf[5] = regNoLSB
    buf[6] = ( val & 255 )
    buf[7] = (val >> 8) & 255

    buf = addChecksumAndLength(buf)

    # print buf

    serial.write(buf)



def sendCmd(serial, addr, cmd):
    buf = np.array([0xFF, 0xFF, 0, 0, 0, 0, 0], dtype=np.uint8)

    buf[2] = addr
    buf[4] = cmd

    buf = addChecksumAndLength(buf)

    serial.write(buf)




def open_dampers(ser, lId, rId):
    bcastAddr = 254


    setReg1(ser, bcastAddr, 25, 1) # LED on
    time.sleep(1)
    setReg1(ser, bcastAddr, 25, 0) # LED off
    time.sleep(1)

    speed = 0x0FF # 0-1023

    opened = 0x1FF # Angle for both servos to be open (wide open)

    langle = opened
    rangle = opened
    setReg2(ser, rId, 32, speed)
    setReg2(ser, rId, 30, rangle)


    setReg2(ser, lId, 32, speed)
    setReg2(ser, lId, 30, langle)

def close_dampers(ser, lId, rId):
    bcastAddr = 254


    setReg1(ser, bcastAddr, 0x19, 1) # LED on
    time.sleep(1)
    setReg1(ser, bcastAddr, 0x19, 0) # LED off
    time.sleep(1)

    speed = 0x0FF # 0-1023

    lClosed = 0x32F # Angle for the servo on the _left_ to be closed
    rClosed = 0x0CA # Angle for the servo on the _right_ to be closed

    langle = lClosed
    rangle = rClosed
    setReg2(ser, rId, 32, speed)
    setReg2(ser, rId, 30, rangle)

    time.sleep(0.01)

    setReg2(ser, lId, 32, speed)
    setReg2(ser, lId, 30, langle)

def set_angle_limit(ser, addr, lower, upper):
    if lower > upper:
        print "lower limit > upper limit", lower, upper
        return False
    setReg2(ser, addr, 0x06, lower)
    setReg2(ser, addr, 0x08, upper)
    return True

def set_return_status(ser, addr, status):
    '''
        Configures how the servo responds to communication:
        0: No response
        1: Respond only to READ
        2: Responds to ALL communication
    '''
    setReg1(ser, addr, 0x10, status)
    return True

def blink_LED(ser, addr):
    '''
        Blink the LED for 1 second
    '''
    setReg1(ser, addr, 0x19, 1) # LED on
    time.sleep(1)
    setReg1(ser, addr, 0x19, 0) # LED off
    return True

def set_addr(ser, addr):
    bcastAddr = 254
    setReg1(ser, bcastAddr, 0x03, addr)
    return True

def set_baud_rate(ser, addr, baud):

    servo_baud = int(round(2000000 / baud)) - 1

    if servo_baud < 1 or 207 < servo_baud:
        print "bad baud rate", baud

    setReg1(ser, addr, 0x04, servo_baud)
    time.sleep(0.01)

    ser.setBaudrate(baud)

    return True



def configure_dampers(ser):

    key = raw_input("Choose servo address (must be unique, and must be the ONLY connected servo. 'n' to abort)\n>>>")
    if (key == 'n'):
        print "aborted"
        return
    addr = int(key)
    print "setting address: ",addr
    set_addr(ser, addr)

    key = raw_input("Servo orientation? r = dampers open cw, l = dampers open ccw \n>>>")
    if key == 'r':
        lower_limit = 0x0CA
        upper_limit = 0x1FF
    elif key == 'l':
        lower_limit = 0x1FF
        upper_limit = 0x32F
    else:
        print "error, orientation must be 'r' or 'l'"
        return
    print "setting angle limits: ",lower_limit, upper_limit
    set_angle_limit(ser, addr, lower_limit, upper_limit)

    key = raw_input("Return Status? 0: None 1: only to READ 2: to ALL \n>>>")
    status = int(key)
    print "setting return status: ",status
    set_return_status(ser, addr, status)

    # key = raw_input("Set baud rate. 1000000 is default, but 9600 is good\n>>>")
    # baud = int(key)
    baud = 9600
    print "setting baud rate to ",baud
    set_baud_rate(ser, addr, baud)

    while True:
        blink_LED(ser, addr)
        if raw_input("Press ENTER to blink LED 'q' to quit\n>>>") == "q":
            break

def test_dampers(ser):
    while True:
        key = raw_input("open or close? ('quit' to abort)\n>>>")
        if key == 'open':
            open_dampers(ser, 1, 2)
        elif key == 'close':
            close_dampers(ser, 1, 2)
        elif key == 'blink':
            blink_LED(ser, 254)
        elif key == 'quit':
            break

if __name__ == "__main__":
    ser = s.Serial(
        port='/dev/ttyUSB0',
        baudrate=1000000,
        parity=s.PARITY_NONE,
        stopbits=s.STOPBITS_ONE,
        bytesize=s.EIGHTBITS,
        timeout=2
    )

    ser.isOpen()

    # sendCmd(ser, bcastAddr, 6) # Reset all servos

    # setReg1(ser, bcastAddr, 3, servoId) # Set address of any servos listening (preferrably just one at a time)
    # lId = 69
    # rId = 6
    #
    # open_dampers(ser, lId, rId)
    # close_dampers(ser, lId, rId)

    # if raw_input("has the servo been configured before? (y/n)\n>>>") == 'y':
    key = raw_input("what is the baud rate?\n>>>")
    baud = int(key)
    print "setting baudrate to ",baud,"\n"
    ser.setBaudrate(baud)

    if raw_input("configure damper servo? (y/n)\n>>>") == 'y':
        configure_dampers(ser)


    test_dampers(ser)
