// By Bjørnar Prytz
#include <Wire.h>           // I2C
#include <SoftwareSerial.h> // Software-implemented Serial Communication
#include "ServoControl.h"   // Servo Communication library
#include "T66CO2.h"         // CO2 sensor Communication
#include "HumTemp.h"        // Hum/Temp sensor Communication

#include <PWM.h>            // For changing the frequency of a pin

#define SERVO_Rx_PIN        11  // Not used, but necessary for the SoftwareSerial interface
#define SERVO_Tx_PIN        10  // Communication with servos is master->slave only
#define T66_1_Rx_PIN        12
#define T66_1_Tx_PIN        13
#define LED_RED_PIN         5
#define LED_WHT_PIN         6
#define LED_BLU_PIN         7
#define FAN_INT_PIN         8   // Internal fans

/*
 *  **Important note on the SoftwareSerial library**
 *  Not all pins on the Mega and Mega 2560 support change interrupts,
 *  so only the following can be used for RX:
 *  10, 11, 12, 13, 50, 51, 52, 53, 62, 63, 64, 65, 66, 67, 68, 69
 */

// Virtual Serial Port
SoftwareSerial T66_Serial(T66_1_Rx_PIN, T66_1_Tx_PIN);

// Servo Communication

SoftwareSerial DamperServos(SERVO_Rx_PIN, SERVO_Tx_PIN);


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

const byte DAMPERS_CLOSED  = 0;
const byte DAMPERS_OPEN    = 1;

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
unsigned long interval = 2000; // 2 seconds between each reading

// Fan Test
unsigned long prevLEDMillis = 0;
unsigned long LEDInterval = 5000;

void setup() {
  Serial.begin(RPi_BAUD);         // With Raspberry Pi
  hum_temp_init();                // join i2c bus (address optional for master)
  T66_Serial.begin(T66_BAUD);     // Opens virtual serial port with the CO2 Sensor
  DamperServos.begin(SERVO_BAUD);
  // for debug
  pinMode(LED_BUILTIN, OUTPUT);

  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_WHT_PIN, OUTPUT);
  pinMode(LED_BLU_PIN, OUTPUT);
  pinMode(FAN_INT_PIN, OUTPUT);
}

byte red = 0;
byte wht = 0;
byte blu = 0;

void loop() {
  byte packet = 0;
  unsigned long currentMillis = millis();
  byte h_t_rsp[TEMP_HUM_RSP_SIZE]; // To hold
  
  
  if (currentMillis - prevLEDMillis > LEDInterval) {
    analogWrite(LED_RED_PIN, red);
    analogWrite(LED_WHT_PIN, wht);
    analogWrite(LED_BLU_PIN, blu);
    
    prevLEDMillis = millis();

    red = (red + 0x10) % 0x100;
    blu = red*2 % 0x100;
    wht = blu*2 % 0x100;
  }

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
    co2_ppm = CO2_reading(&T66_Serial, interval/2);  // Spend at most half an interval here
    previousMillis = currentMillis;

    digitalWrite(LED_BUILTIN, LOW);
  }
}

void handle_instruction(byte packet) {
  if (packet == TEMPERATURE) {
    RPi_get_temperature();
  } else if (packet == HUMIDITY) {
    RPi_get_humidity();
  } else if (packet == CO2) {
    RPi_get_co2();
  } else if (packet == FAN_SPEED) {
    if (set_fan_speed())
      send_ack(packet);
    else
      send_error(packet);
  } else if (packet == SERVOS) {
    if (set_servos())
      send_ack(packet);
    else
      send_error(packet);
  } else if (packet == LED_RED) {
    set_LED(RED);
  } else if (packet == LED_WHT) {
    set_LED(WHITE);
  } else if (packet == LED_BLU) {
    set_LED(BLUE);
  }
}

bool RPi_wait_and_listen(unsigned int timeout) {
  while (timeout > 0) {
    if (Serial.available() > 0)
      return true;
    delay(100);
    timeout -= 1;
  }
  return false;
}

byte get_data(byte packet)
{
  // Because the most significant bit is used for control, we can reach a larger range
  // by omitting the least significant bit instead.
  return packet << 1;  
}

void send_ack(byte packet)
{
  Serial.write(packet | CONTROL_MASK); // Rebuild the instruction packet to signify success
}

void send_error(byte packet)
{
  Serial.write(packet & VALUE_MASK); // Mask out the control bit to signify an error
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

bool set_fan_speed() {
  byte packet;

  if (RPi_wait_and_listen(10)) { // Wait 1 second for follow-up data
    packet = Serial.read();
    if (is_data(packet)) {
      analogWrite(FAN_INT_PIN, get_data(packet));
      return true;
    }
  }
  return false;
}

bool set_servos() {
  byte sig; // Signal from the Raspberry Pi. 0: close dampers, 1: open dampers

  if (RPi_wait_and_listen(10)) { // Wait 1 second for follow-up data
    sig = Serial.read() & VALUE_MASK;
    if (sig == DAMPERS_OPEN) open_dampers(&DamperServos, LEFT_ADDR, RIGHT_ADDR);
    else if (sig == DAMPERS_CLOSED) close_dampers(&DamperServos, LEFT_ADDR, RIGHT_ADDR);
    else return false;
    return true;
  }
  return false;
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
