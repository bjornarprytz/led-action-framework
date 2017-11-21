#ifndef ServoControl_h
#define ServoControl_h

#include "Arduino.h"
#include <SoftwareSerial.h>

// Servo Settings
#define SERVO_Rx      11  // Not used, but necessary for the SoftwareSerial interface
#define SERVO_Tx      10
#define SERVO_BAUD    9600
#define LEFT_ADDR     1
#define RIGHT_ADDR    2
#define LEFT_OPEN     0x1FF
#define LEFT_CLOSED   0x32F
#define RIGHT_OPEN    0x1FF
#define RIGHT_CLOSED  0x0CA
#define SPEED         0x0FF


void addChecksumAndLength(byte *buf, byte len);
void setReg1(SoftwareSerial *com, byte addr, byte regNo, byte val);
void setReg2(SoftwareSerial *com, byte addr, byte regNoLSB, int val);
void open_dampers(SoftwareSerial *com, byte addr_left, byte addr_right);
void close_dampers(SoftwareSerial *com, byte addr_left, byte addr_right);
void blink_led(SoftwareSerial *com, byte addr);


#endif
