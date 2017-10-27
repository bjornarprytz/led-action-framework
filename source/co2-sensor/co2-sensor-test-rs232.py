import time
import serial
import numpy as np

class Msg:
    def __init__(self):
        self.flag = 0xFF
        self.address = 0xFE # General address (all sensors will respond)
        self.length = 0x02
        self.command = 0x00 # Loopback: echoes back with the bytes that follow
        self.additional_data = 0x00

    def get_message(self):
        # msg = self.get_flag() + self.get_address() + self.get_length() + self.get_command()

        msg = np.array([self.flag, self.address, self.length, self.command, self.additional_data], dtype=np.uint8)

        return msg

    def get_flag(self):
        return (self.flag << (8 * (self.length + 2)))

    def get_address(self):
        return (self.address << (8 * (self.length + 1)))

    def get_length(self):
        return (self.length << (8 * (self.length)))

    def get_command(self):
        return (self.command << (8 * (self.length - 1)))

    def get_additional_data(self):
        return (self.additional_data << (8 * (self.length-2)))

    def set_command(self, command, additional_data=0x01):
        self.command = command
        self.additional_data = additional_data
        self.length = 0x02

def read_response(serial):
    hdr_len = 3
    header = np.frombuffer(serial.read(hdr_len), dtype=np.uint8)

    pl_len = header[-1]
    payload = np.frombuffer(serial.read(pl_len), dtype=np.uint8)

    response = np.concatenate((header, payload))

    print response


# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

ser.isOpen()

message = Msg()
message.set_command(0x02, 0x01)

packet = message.get_message()
print packet
ser.write(packet)

time.sleep(1)
print "waiting for response..."

read_response(ser)
# out = ser.read(1)
# print np.frombuffer(out, dtype=np.uint8)
# print "waiting for response..."
# out = ser.read(1)
# print np.frombuffer(out, dtype=np.uint8)
