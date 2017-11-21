#ifndef HumTemp_h
#define HumTemp_h

#include "Arduino.h"
#include <Wire.h>           // I2C

#define HUM_TEMP_ADDRESS 0x28
#define TEMP_HUM_RSP_SIZE 4 // Humidity and temperature data is 4 bytes

void hum_temp_init();
void hum_temp_reading(char address, byte *buf);
float get_hum_from_reading(byte *buf);
float get_temp_from_reading(byte *buf);

#endif
