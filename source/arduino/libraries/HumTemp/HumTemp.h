#ifndef HumTemp_h
#define HumTemp_h

#include "Arduino.h"
#include <Wire.h>           // I2C

#define HUM_TEMP_ADDRESS 0x28
#define TEMP_HUM_RSP_SIZE 4 // Humidity and temperature data is 4 bytes

// Initialises i2c interface Wire.h
void hum_temp_init();
// Gets a reading from the sensor and stores the response in a buffer
void hum_temp_reading(char address, byte *buf);
// Extracts humidity from the input buffer
float get_hum_from_reading(byte *buf);
// Extracts the temperature from the input buffer
float get_temp_from_reading(byte *buf);

#endif
