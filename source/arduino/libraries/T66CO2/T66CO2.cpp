#include "Arduino.h"
#include "T66CO2.h"

byte readCO2[] = {0xFF, 0xFE, 0x02, 0x02, 0x03}; // Read co2 command
byte readStatus[] = {0xFF, 0xFE, 0x01, 0xB6}; // Read status byte


bool is_warming_up(SoftwareSerial *com) {
  if (sensor_status(com, 25) & WARM_UP_FLAG) {
    return true;
  } else {
    return false;
  }
}

bool set_elevation(SoftwareSerial *com, int value) {
  byte lsb = value % 0x100; // 256
  byte msb = value >> 8;

  byte command[] = {0xFF, 0xFE, 0x03, 0x0F, msb, lsb};
  byte response[] = {1,1,1};
  int cmd_size = 6;
  int rsp_size = 3;

  int retries = 3;
  while (!T66_sendCommand(com, command, response, cmd_size, rsp_size)) {
    retries--;
    if (retries < 0)
      return false;
    delay(30); // Avoid flooding the Sensor with requests
  }

  if (response[rsp_size-1] == 0x00) { // Validate the ACK
    return true;
  }
  return false;
}

bool start_warmup(SoftwareSerial *com) {
  byte command[] = {0xFF, 0xFE, 0x01, 0x84};
  byte* response;

  int cmd_size = 4;
  int rsp_size = 0;
  T66_sendCommand(com, command, response, cmd_size, rsp_size);
}

byte sensor_status(SoftwareSerial *com, unsigned long grace) {
  unsigned long start = millis();
  com->listen(); // In case there are several devices connected via SoftwareSerial, activate this one
  byte response[] = {0,0,0,0}; // 4 byte array to hold the response
  int cmd_size = 4;
  int rsp_size = 4;
  while (!T66_sendCommand(com, readStatus, response, cmd_size, rsp_size)) {
    if (millis() - start > grace)
      return;
      delay(10); // Avoid flooding the Sensor with requests
  }
  return response[3];
}

float CO2_reading(SoftwareSerial *com, unsigned long grace) {
  unsigned long start = millis();
  com->listen(); // In case there are several devices connected via SoftwareSerial, activate this one
  byte response[] = {0,0,0,0,0}; // 5 byte array to hold the response
  int cmd_size = 5;
  int rsp_size = 5;
  while (!T66_sendCommand(com, readCO2, response, cmd_size, rsp_size)) {
    if (millis() - start > grace)
      return;
      delay(30); // Avoid flooding the Sensor with requests
  }
  return (float)T66_getValue(response);
}

unsigned long T66_getValue(byte packet[]) {
  // by Marv kausch @ Co2meter.com
  int high = packet[3]; //high byte for value is 4th byte in packet in the packet
  int low = packet[4]; //low byte for value is 5th byte in the packet
  unsigned long val = high*256 + low; //Combine high byte and low byte with this formula to get value
  return val;
}

bool T66_sendCommand(SoftwareSerial *com, byte command[], byte response[], int cmd_size, int rsp_size) {
  // by Marv kausch @ Co2meter.com
  if (!com->available()) {   // keep sending request until we start to get a response
    com->write(command,cmd_size);   // Write command to sensor
    return false; // Exit and try again
  }
  int timeout=0; //set a timeoute counter
  while(com->available() < rsp_size ) { //Wait to get a 7 byte response
    timeout++;
    if(timeout > 10) { //if it takes too long there was probably an error
      Serial.print("Timeout");

      while(com->available()) // whatever we have
        com->read();                 // - flush it
      return false; //exit and try again
    }
  delay(30);
  }
  for (int i=0; i < rsp_size; i++)
    response[i] = com->read();
  return true;
}
