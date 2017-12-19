// By Bjørnar Prytz
#include <Wire.h>           // I2C
#include <SoftwareSerial.h> // Software-implemented Serial Communication
#include "ServoControl.h"   // Servo Communication library
#include "T66CO2.h"         // CO2 sensor Communication
#include "HumTemp.h"        // Hum/Temp sensor Communication

#define LED_RED_PIN         5
#define LED_WHT_PIN         6
#define LED_BLU_PIN         7
#define FAN_INT_PIN         8   // Internal fans
#define FAN_EXT_PIN         9   // External fans
#define SERVO_Rx_PIN        11  // Not used, but necessary for the SoftwareSerial interface
#define SERVO_Tx_PIN        10  // Communication with servos is master->slave only
#define T66_1_Rx_PIN        12
#define T66_1_Tx_PIN        13


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

// Handshake masks
const byte CONTROL_MASK = 0xF0; // 1010xxxx indicates a handshake byte
const byte SIZE_MASK    = 0x0F; // xxxx1111 contains the number of bytes following the header

const byte HEADER_FLAG  = 0B10100000;

// instruction description
const byte TEMPERATURE  = 0x00;
const byte HUMIDITY     = 0x01;
const byte CO2          = 0x02;
const byte FAN_INT      = 0x03;
const byte FAN_EXT      = 0x04;
const byte SERVOS       = 0x05;
const byte LED          = 0x06;


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
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  
  Serial.begin(RPi_BAUD);         // With Raspberry Pi
  hum_temp_init();                
  T66_Serial.begin(T66_BAUD);     // Opens virtual serial port with the CO2 Sensor
  DamperServos.begin(SERVO_BAUD);
  
  // for debug
  digitalWrite(LED_BUILTIN, LOW);
  analogWrite(FAN_INT_PIN, 0);
  analogWrite(FAN_EXT_PIN, 0);
}

void loop() {
  unsigned long currentMillis = millis();
  
  listen_for_handshake();

  update_data(currentMillis);  
}



void update_data(unsigned long currentMillis) {
  byte h_t_rsp[TEMP_HUM_RSP_SIZE]; // To hold humidity/temperature readings
  
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


void listen_for_handshake() {
  byte header = 0;

  if (Serial.available() > 0) {
    header = Serial.read();    
    validate_and_handle_msg(header);
  }
}

void handle_instruction(byte instruction, byte* payload, unsigned int s) {
  
  if (instruction == TEMPERATURE) {
    RPi_send_float(TEMPERATURE, temperature);
    
  } else if (instruction == HUMIDITY) {
    RPi_send_float(HUMIDITY, humidity);
    
  } else if (instruction == CO2) {
    RPi_send_float(CO2, co2_ppm);
    
  } else if (instruction == FAN_INT) {
    if (set_internal_fan_speed(payload, s))
      send_ack(instruction);
    else
      send_error(instruction);
      
  } else if (instruction == FAN_EXT) {
    if (set_external_fan_speed(payload, s))
      send_ack(instruction);
    else
      send_error(instruction);
  } else if (instruction == SERVOS) {
    if (set_servos(payload, s))
      send_ack(instruction);
    else
      send_error(instruction);
      
  } else if (instruction == LED) {
    if (set_LED(payload, s)) 
      send_ack(instruction);
    else 
      send_error(instruction);
  }
}

void validate_and_handle_msg(byte header) {
  if (!is_valid_header(header)) return;
  
  unsigned int s = get_size(header);

  if (s < 2) return;

  byte* msg = (byte *)malloc(sizeof(byte)*s);

  Serial.readBytes(msg, s);

  if (validate_checksum(msg, s)) {
    byte instruction = msg[0];
    byte *payload = &msg[1];
    unsigned int pl_size = s - 2;
    
    handle_instruction(instruction, payload, pl_size);
  }

  free(msg);
}

bool validate_checksum(byte* payload, unsigned int s) {
  byte cs = 0;

  for (int i=0; i<s-1; i++) { 
    cs += payload[i];
  }

  cs %= 0x100;

  if (payload[s-1] == cs) return true;
  else return false;
}


void send_ack(byte packet)
{
  Serial.write(packet); // Return the instruction packet to signify success
}

void send_error(byte packet)
{
  Serial.write(~packet); // Return a negated instruction to signify an error
}

bool is_valid_header(byte packet) {
  if ((packet & CONTROL_MASK) == HEADER_FLAG) return true;
  else return false;
}

unsigned int get_size(byte packet) {
  return packet & SIZE_MASK;
}

void RPi_send_byte(byte type, byte data) {
  send_ack(type);
  Serial.write(data);
}

void RPi_send_float(byte type, float data) {
  String buf = String(data);
  send_ack(type);
  Serial.println(buf);
}

bool set_internal_fan_speed(byte* payload, unsigned int s) {
  return set_fan_speed(payload, s, FAN_INT_PIN);
}

bool set_external_fan_speed(byte* payload, unsigned int s) {
  return set_fan_speed(payload, s, FAN_EXT_PIN);
}

bool set_fan_speed(byte* payload, unsigned int s, int pin_num) {
  if (s < 1) return false;
  byte spd = payload[0]; // Only use 1 byte
  analogWrite(pin_num, spd);
  return true;
}

bool set_servos(byte* payload, unsigned int s) {
  if (s < 1) return false;

  byte signl = payload[0]; // Signal from the Raspberry Pi. 0: close dampers, 1: open dampers

  if (signl == DAMPERS_OPEN) open_dampers(&DamperServos, LEFT_ADDR, RIGHT_ADDR);
  else if (signl == DAMPERS_CLOSED) close_dampers(&DamperServos, LEFT_ADDR, RIGHT_ADDR);

  return true;
}

bool set_LED(byte* payload, unsigned int s) {
  byte packet;

  if (s < 3) return false;

  byte red = payload[0];
  byte white = payload[1];
  byte blue = payload[2];

  analogWrite(LED_RED_PIN, red);
  analogWrite(LED_WHT_PIN, white);
  analogWrite(LED_BLU_PIN, blue);

  return true;
}
