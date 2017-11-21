#include "Arduino.h"
#include "ServoControl.h"

void addChecksumAndLength(byte *buf, byte len)
{
    // adding length
    buf[3] = len - 4;

    byte tmp;
    // finding sum
    byte checksum = 0;
    for (int i=2;i<len-1; i++) {
      tmp = buf[i];
      if (tmp < 0)
        tmp = tmp + 256;
      checksum += tmp;
    }
    // inverting bits
    checksum = ~checksum;
    // int2byte
    checksum = checksum & 255;

    // adding checkSum
    buf[len-1] = checksum;
}

void setReg1(SoftwareSerial *com, byte addr, byte regNo, byte val)
{
  byte buf[] = {0xFF, 0xFF, 0, 0, 0x3, 0, 0, 0};

  buf[2] = addr;
  buf[5] = regNo;
  buf[6] = val;

  addChecksumAndLength((char*)&buf, sizeof(buf)/sizeof(buf[0]));

  com->write(buf, sizeof(buf));
}

void setReg2(SoftwareSerial *com, byte addr, byte regNoLSB, int val)
{
  byte buf[] = {0xFF, 0xFF, 0, 0, 0x3, 0, 0, 0, 0};

  buf[2] = addr;
  buf[5] = regNoLSB;
  buf[6] = ( val & 255 );
  buf[7] = (val >> 8) & 255;

  addChecksumAndLength((char*)&buf, sizeof(buf)/sizeof(buf[0]));

  com->write(buf, sizeof(buf));
}
void open_dampers(SoftwareSerial *com, byte addr_left, byte addr_right)
{
  com->listen();

  setReg2(com, addr_left, 0x20, SPEED);
  setReg2(com, addr_left, 0x1E, LEFT_OPEN);

  setReg2(com, addr_right, 0x20, SPEED);
  setReg2(com, addr_right, 0x1E, RIGHT_OPEN);
}

void close_dampers(SoftwareSerial *com, byte addr_left, byte addr_right)
{
  com->listen();

  setReg2(com, addr_left, 0x20, SPEED);
  setReg2(com, addr_left, 0x1E, LEFT_CLOSED);

  setReg2(com, addr_right, 0x20, SPEED);
  setReg2(com, addr_right, 0x1E, RIGHT_CLOSED);
}

void blink_led(SoftwareSerial *com, byte addr)
{
  com->listen();

  setReg1(com, addr, 0x19, 1);
  delay(1000);
  setReg1(com, addr, 0x19, 0);
}
