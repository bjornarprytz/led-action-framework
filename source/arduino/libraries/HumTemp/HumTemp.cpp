#include "Arduino.h"
#include "HumTemp.h"

void hum_temp_init() {
  Wire.begin();
}

void hum_temp_reading(char address, byte *buf) {
// Wire Master Reader
// by Nicholas Zambetti <http://www.zambetti.com>

  // Signal the device to do a reading
  Wire.beginTransmission(address);
  Wire.write(1);
  Wire.endTransmission();

  delay(60); // Wait for the sensor to do the task

  Wire.requestFrom(address, TEMP_HUM_RSP_SIZE);

  buf[0] = Wire.read();
  buf[1] = Wire.read();
  buf[2] = Wire.read();
  buf[3] = Wire.read();
}

float get_hum_from_reading(byte *buf) {
  return (float)(((buf[0] & 0x3f) << 8 | buf[1]) * (100.0 / 0x3fff));
}

float get_temp_from_reading(byte *buf) {
  return (float)((buf[2] << 8 | (buf[3] & 0xfc)) * (165.0 / 0xfffc) - 40);
}
