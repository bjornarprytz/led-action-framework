#ifndef T66O2_h
#define T66O2_h

#include "Arduino.h"
#include "SoftwareSerial.h"

// T6613 Telaire(CO2) Communication
#define T66_BAUD 19200

// Top level function that tries the sensor for [grace] amount of milliseconds
float CO2_reading(SoftwareSerial *com, unsigned long grace);
// Sends a request over the SoftwareSerial interface and stores the response in the input buffer
bool T66_sendRequest(SoftwareSerial *com, byte request[], byte response[]);
// Extracts the CO2 ppm from the input packet.
unsigned long T66_getValue(byte packet[]);


#endif
