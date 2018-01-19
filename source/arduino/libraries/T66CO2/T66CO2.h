#ifndef T66O2_h
#define T66O2_h

#include "Arduino.h"
#include "SoftwareSerial.h"

// T6613 Telaire(CO2) Communication
#define T66_BAUD 19200
#define WARM_UP_FLAG 0x02

// If the sensor is warming up, it should not be used yet
bool is_warming_up(SoftwareSerial *com);
// Set the elevation level of the sensor. Factors into ppm calculations
bool set_elevation(SoftwareSerial *com, int value);
// Resets the sensor and starts the warmup sequence
bool start_warmup(SoftwareSerial *com);
// Get a byte which includes the various status flags in the T6613 Telaire sensor
byte sensor_status(SoftwareSerial *com, unsigned long grace);
// Top level function that tries the sensor for [grace] amount of milliseconds
float CO2_reading(SoftwareSerial *com, unsigned long grace);
// Sends a request over the SoftwareSerial interface and stores the response in the input buffer
bool T66_sendCommand(SoftwareSerial *com, byte request[], byte response[], int req_size, int rsp_size);
// Extracts the CO2 ppm from the input packet.
unsigned long T66_getValue(byte packet[]);


#endif
