#ifndef ServoControl_h
#define ServoControl_h

#include "Arduino.h"
#include <SoftwareSerial.h>

// Servo Settings
#define SERVO_BAUD      9600
#define LEFT_ADDR       1
#define RIGHT_ADDR      2
#define LEFT_OPEN       0x1FF
#define LEFT_CLOSED     0x32F
#define RIGHT_OPEN      0x1FF
#define RIGHT_CLOSED    0x0CA
#define SPEED           0x0FF
#define SPEED_REG_ADDR  0x20
#define POS_REG_ADDR    0x1E

// Adds checksum and length to a Dynamixel instruction
void addChecksumAndLength(byte *buf, byte len);
// Write val to a specific register. List of registers: (http://www.crustcrawler.com/products/bioloid/docs/AX-12.pdf)
void setReg1(SoftwareSerial *com, byte addr, byte regNo, byte val);
// Some values need two subsequent registers
void setReg2(SoftwareSerial *com, byte addr, byte regNoLSB, int val);
// System specific function to open dampers to a 90 degree angle
void open_dampers(SoftwareSerial *com, byte addr_left, byte addr_right);
void close_dampers(SoftwareSerial *com, byte addr_left, byte addr_right);
// For debugging. Blinks the LED on the servos. May use address 254 to broadcast
void blink_led(SoftwareSerial *com, byte addr);


#endif
