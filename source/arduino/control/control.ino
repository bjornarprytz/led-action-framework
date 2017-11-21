// By Bjørnar Prytz
#include <Wire.h>           // I2C
#include <SoftwareSerial.h> // Software-implemented Serial Communication
#include "ServoControl.h"   // Servo Communication library
#include "T66CO2.h"         // CO2 sensor Communication
#include "HumTemp.h"        // Hum/Temp sensor Communication

// Virtual Serial Port
SoftwareSerial T66_Serial(T66_1_Rx, T66_1_Tx);

// Servo Communication
SoftwareSerial DamperServos(SERVO_Rx, SERVO_Tx);

// Raspberry Pi Communication
#define RPi_BAUD 9600

const byte CONTROL_MASK = B10000000;
const byte VALUE_MASK   = B01111111;

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

// For output:
float temperature = 0.0;
float humidity = 0.0;
float co2_ppm = 0.0;
byte LED_red   = 0;
byte LED_white = 0;
byte LED_blue  = 0;

// State Machine
unsigned long previousMillis = 0;
unsigned long interval = 4000; // 4 seconds between each reading

void setup() {
  Serial.begin(RPi_BAUD);         // With Raspberry Pi
  hum_temp_init();               // join i2c bus (address optional for master)
  T66_Serial.begin(T66_BAUD);     // Opens virtual serial port with the CO2 Sensor
  DamperServos.begin(SERVO_BAUD);
  // for debug
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  byte packet = 0;
  unsigned long currentMillis = millis();
  byte h_t_rsp[TEMP_HUM_RSP_SIZE]; // To hold

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

    hum_temp_reading(HUM_TEMP_ADDRESS, (char*)&h_t_rsp);
    humidity = get_hum_from_reading((char*)&h_t_rsp);
    temperature = get_temp_from_reading((char*)&h_t_rsp);
    co2_ppm = CO2_reading(&T66_Serial, 2000);  // Spend at most 2 seconds here
    previousMillis = currentMillis;

    digitalWrite(LED_BUILTIN, LOW);
  }
}

void handle_instruction(byte packet) {
  byte sig;
  if (packet == TEMPERATURE) {
    RPi_get_temperature();
  } else if (packet == HUMIDITY) {
    RPi_get_humidity();
  } else if (packet == CO2) {
    RPi_get_co2();
  } else if (packet == FAN_SPEED) {
    set_fan_speed();
  } else if (packet == SERVOS) {
    sig = set_servos();
    if (sig == 1) open_dampers(&DamperServos, LEFT_ADDR, RIGHT_ADDR);
    else close_dampers(&DamperServos, LEFT_ADDR, RIGHT_ADDR);
    send_ack(packet);
  } else if (packet == LED_RED) {
    set_LED(RED);
  } else if (packet == LED_WHT) {
    set_LED(WHITE);
  } else if (packet == LED_BLU) {
    set_LED(BLUE);
  }
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

void send_ack(byte packet)
{
  Serial.write(packet | CONTROL_MASK);
}

bool is_instruction(byte packet) {
  return packet & CONTROL_MASK; // Check the most significant bit (1 = instruction)
}

bool is_data(byte packet) {
  return !(packet & CONTROL_MASK); // Check the most significant bit (0 = data)
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
      ; // TODO: signal actuator
    }
  }
}

byte set_servos() {
  byte packet;

  if (RPi_wait_and_listen(10)) { // Wait 1 second for follow-up data
    packet = Serial.read();
    return packet;
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
