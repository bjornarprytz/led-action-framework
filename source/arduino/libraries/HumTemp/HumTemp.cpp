#include "Arduino.h"
#include "HumTemp.h"

void hum_temp_init() {

  Wire.begin(); // join i2c bus (address optional for master)
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
  byte msb = buf[0] & 0x3f; // Only need 14 bits total (mask: 00111111)
  byte lsb = buf[1];

  float adjusted_humidity = (float)((msb << 8 | lsb) * (100.0 / 0x3fff)); // adjust the reading to a percentage (0-100)

  return adjusted_humidity;
  //   return (float)(((buf[0] & 0x3f) << 8 | buf[1]) * (100.0 / 0x3fff));
}

float get_temp_from_reading(byte *buf) {
  byte msb = buf[2];
  byte lsb = buf[3] & 0xfc;

  float adjusted_temp = (float)((msb << 8 | lsb) * (165.0 / 0xfffc)-40); // adjust the reading to the range -40-125 degrees celcius

  return adjusted_temp;
  // return (float)((buf[2] << 8 | (buf[3] & 0xfc)) * (165.0 / 0xfffc) - 40);
}
