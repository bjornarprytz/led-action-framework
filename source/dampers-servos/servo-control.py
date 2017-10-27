import serial as s
import numpy as np
import time

def addChecksumAndLength(buf):
    # adding length
    print "size: ", buf.size
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

    print checksum
    print buf
    return buf



 # ======================= Writes 0<val<255 to register "regNo" in servo "id" ======================

def setReg1(serial, id, regNo, val):
    buf = np.array([0xFF, 0xFF, 0, 0, 0x3, 0, 0, 0], dtype=np.uint8)

    buf[2] = id
    buf[5] = regNo
    buf[6] = val

    buf = addChecksumAndLength(buf)

    print buf

    serial.write(buf)

 # ======================= Writes 0<val<1023 to register "regNoLSB/regNoLSB+1" in servo "id" =======

def setReg2(serial, id, regNoLSB, val):
    buf = np.array([0xFF, 0xFF, 0, 0, 0x3, 0, 0, 0, 0], dtype=np.uint8)

    buf[2] = id
    buf[5] = regNoLSB
    buf[6] = ( val & 255 )
    buf[7] = (val >> 8) & 255

    buf = addChecksumAndLength(buf)

    print buf

    serial.write(buf)



def sendCmd(serial, id, cmd):
    buf = np.array([0xFF, 0xFF, 0, 0, 0, 0, 0], dtype=np.uint8)

    buf[2] = id
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


    setReg1(ser, bcastAddr, 25, 1) # LED on
    time.sleep(1)
    setReg1(ser, bcastAddr, 25, 0) # LED off
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
    lId = 69
    rId = 6

    open_dampers(ser, lId, rId)
    close_dampers(ser, lId, rId)
