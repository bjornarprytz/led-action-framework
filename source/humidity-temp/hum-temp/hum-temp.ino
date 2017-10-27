// Wire Master Reader
// by Nicholas Zambetti <http://www.zambetti.com>

// Demonstrates use of the Wire library
// Reads data from an I2C/TWI slave device
// Refer to the "Wire Slave Sender" example for use with this

// Sensor -> Red -> Red -> 5V
// Sensor -> Brown -> Green -> SCL 21
// Sensor -> Purple -> Yellow -> SDA 20
// Sensor -> Black -> Black -> GND


const char device_address = 0x28;

#include <Wire.h>

void take_reading(char address) {
  int RSP_SIZE = 4; // Humidity / temperature data is 4 bytes
  float hum, temp;
  byte data[RSP_SIZE];
  
  // Signal the device to do a reading
  Wire.beginTransmission(address);
  Wire.write(1);
  Wire.endTransmission();

  delay(60); // Wait for the sensor to do the task
  
  Wire.requestFrom(address, RSP_SIZE);
  
  data[0] = Wire.read();
  data[1] = Wire.read();
  data[2] = Wire.read();
  data[3] = Wire.read();
  
  
  hum = ((data[0] & 0x3f) << 8 | data[1]) * (100.0 / 0x3fff);
  temp = (data[2] << 8 | (data[3] & 0xfc)) * (165.0 / 0xfffc) - 40;

  Serial.print("Humidity: ");
  Serial.println(hum, 4);
  Serial.print("Temperature: ");
  Serial.println(temp, 4);
}

void setup() {
  
  Wire.begin();        // join i2c bus (address optional for master)
  Serial.begin(4800);  // start serial for output

}

void loop() {
  
  take_reading(device_address);

  delay(5000);
}
