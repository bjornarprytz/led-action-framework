// By Bjørnar Prytz

#include <Wire.h>           // I2C
#include <SoftwareSerial.h> // Software-implemented Serial Communication

// T6613 Telaire(CO2) Communication

#define T66_BAUD 19200
byte readCO2[] = {0xFF, 0XFE,2,2,3}; // Read co2 command

// Virtual Serial Port where 12=Rx and 13=Tx
SoftwareSerial T66_Serial(12,13);

// Temperature/Humidity Communication
const char device_address = 0x28;

// Raspberry Pi Communication
#define RPi_BAUD 9600

const byte CONTROL_MASK = B10000000;

// 7 bit instruction description
const byte TEMPERATURE  = B0000000;
const byte HUMIDITY     = B0000001;
const byte CO2          = B0000010;
const byte FAN_SPEED    = B0000011;
const byte SERVOS       = B0000100;
const byte LED_RED      = B0000101;
const byte LED_WHT      = B0000110;
const byte LED_BLU      = B0000111;

const byte RED = 0;
const byte WHITE = 1;
const byte BLUE = 2;

float temperature = 0.0;
float humidity = 0.0;
float co2_ppm = 0.0;

// State Machine
unsigned long previousMillis = 0;
unsigned long interval = 4000; // 4 seconds between each reading

// For output:
byte fan_speed = 0;
byte servo_pos = 0;
byte LED_red   = 0;
byte LED_white = 0;
byte LED_blue  = 0;


void setup() {
  Serial.begin(RPi_BAUD); // With Raspberry Pi
  Wire.begin();           // join i2c bus (address optional for master)
  T66_Serial.begin(T66_BAUD);   // Opens virtual serial port with the CO2 Sensor

  // for debug
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  byte packet = 0;
  unsigned long currentMillis = millis();



  if (Serial.available() > 0) {
    packet = Serial.read();

    if (is_instruction(packet)) {

      packet %= 0x80;             // Remove the instruction bit
      handle_instruction(packet); // and handle the instruction

    } else {
      Serial.println("got an unexpected non-instruction");
    }
  }

  if (currentMillis - previousMillis > interval) {
    digitalWrite(LED_BUILTIN, HIGH);

    hum_temp_reading(device_address);
    CO2_reading(&T66_Serial, 2000);  // Spend at most 2 seconds here
    previousMillis = currentMillis;

    digitalWrite(LED_BUILTIN, LOW);
  }
}

void CO2_reading(SoftwareSerial *com, unsigned long grace) {
  unsigned long start = millis();

  byte response[] = {0,0,0,0,0}; // 5 byte array to hold the response
  while (!T66_sendRequest(com, readCO2, response)) {
    if (millis() - start > grace)
      return;
    delay(450);
  }
  co2_ppm = (float)T66_getValue(response);
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

void hum_temp_reading(char address) {
// Wire Master Reader
// by Nicholas Zambetti <http://www.zambetti.com>
  int RSP_SIZE = 4; // Humidity / temperature data is 4 bytes
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


  humidity = ((data[0] & 0x3f) << 8 | data[1]) * (100.0 / 0x3fff);
  temperature = (data[2] << 8 | (data[3] & 0xfc)) * (165.0 / 0xfffc) - 40;
}


bool RPi_wait_and_listen(unsigned int patience) {
  while (patience > 0) {
    if (Serial.available() > 0)
      return true;
    delay(100);
    patience -= 1;
  }
  return false;
}

bool is_instruction(byte packet) {
  return packet & CONTROL_MASK; // Check the most significant bit (1 = instruction)
}

bool is_data(byte packet) {
  return !(packet & CONTROL_MASK); // Check the most significant bit (0 = data)
}

void handle_instruction(byte packet) {
  if (packet == TEMPERATURE) {
    RPi_get_temperature();
  } else if (packet == HUMIDITY) {
    RPi_get_humidity();
  } else if (packet == CO2) {
    RPi_get_co2();
  } else if (packet == FAN_SPEED) {
    set_fan_speed();
  } else if (packet == SERVOS) {
    set_servos();
  } else if (packet == LED_RED) {
    set_LED(RED);
  } else if (packet == LED_WHT) {
    set_LED(WHITE);
  } else if (packet == LED_BLU) {
    set_LED(BLUE);
  }
}

void RPi_send_byte(byte type, byte data) {
  Serial.write(type);
  Serial.write(data);
}

void RPi_send_float(byte type, float data) {
  String buf = String(data);
  Serial.write(type);
  Serial.println(buf);
}

void RPi_get_temperature() {
  RPi_send_float(TEMPERATURE, temperature);
}

void RPi_get_humidity() {
  RPi_send_float(HUMIDITY, humidity);
}

void RPi_get_co2() {
  RPi_send_float(CO2, co2_ppm);
}

void set_fan_speed() {
  byte packet;

  if (RPi_wait_and_listen(10)) { // Wait 1 second for follow-up data
    packet = Serial.read();
    if (is_data(packet)) {
      fan_speed = packet; // TODO: signal actuator
    }
  }
}

void set_servos() {
  byte packet;

  if (RPi_wait_and_listen(10)) { // Wait 1 second for follow-up data
    packet = Serial.read();
    if (is_data(packet)) {
      servo_pos = packet; // TODO: signal actuator
    }
  }
}

void set_LED(byte color) {
  byte packet;

  switch (color) {
    case RED:
      if (RPi_wait_and_listen(10)) { // Wait 1 second for follow-up data
        packet = Serial.read();
        if (is_data(packet)) {
          LED_red = packet; // TODO: signal actuator
        }
      }
      break;
    case WHITE:
      if (RPi_wait_and_listen(10)) { // Wait 1 second for follow-up data
        packet = Serial.read();
        if (is_data(packet)) {
          LED_white = packet; // TODO: signal actuator
        }
      }
      break;
    case BLUE:
      if (RPi_wait_and_listen(10)) { // Wait 1 second for follow-up data
        packet = Serial.read();
        if (is_data(packet)) {
          LED_blue = packet; // TODO: signal actuator
        }
      }
      break;
  }
}
