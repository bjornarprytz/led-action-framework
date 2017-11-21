#include "Arduino.h"
#include "T66CO2.h"

byte readCO2[] = {0xFF, 0XFE,2,2,3}; // Read co2 command

float CO2_reading(SoftwareSerial *com, unsigned long grace) {
  unsigned long start = millis();
  com->listen(); // In case there are several devices connected via SoftwareSerial, activate this one
  byte response[] = {0,0,0,0,0}; // 5 byte array to hold the response
  while (!T66_sendRequest(com, readCO2, response)) {
    if (millis() - start > grace)
      return;
    delay(450);
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

bool T66_sendRequest(SoftwareSerial *com, byte request[], byte response[]) {
  // by Marv kausch @ Co2meter.com
  if (!com->available()) {   // keep sending request until we start to get a response
    com->write(request,5);   // Write to sensor 5 byte command
    return false;
  }
  int timeout=0; //set a timeoute counter
  while(com->available() < 5 ) { //Wait to get a 7 byte response
    timeout++;
    if(timeout > 10) { //if it takes too long there was probably an error
      Serial.print("Timeout");

      while(com->available()) // whatever we have
        com->read();                 // - flush it
      return false; //exit and try again
    }
  delay(50);
  }
  for (int i=0; i < 5; i++)
    response[i] = com->read();
  return true;
}
