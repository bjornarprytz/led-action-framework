#ifndef T66O2_h
#define T66O2_h

#include "Arduino.h"
#include "SoftwareSerial.h"

// T6613 Telaire(CO2) Communication
#define T66_BAUD 19200
#define T66_1_Rx 12
#define T66_1_Tx 13

float CO2_reading(SoftwareSerial *com, unsigned long grace);
unsigned long T66_getValue(byte packet[]);
bool T66_sendRequest(SoftwareSerial *com, byte request[], byte response[]);


#endif
