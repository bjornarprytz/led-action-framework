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
#define T66_1_Rx_PIN        12  // Internal CO2 sensor receiver
#define T66_1_Tx_PIN        13  // Internal CO2 sensor transmitter
#define T66_2_Tx_PIN        50  // External CO2 sensor transmitter
#define T66_2_Rx_PIN        51  // External CO2 sensor receiver


/*
 *  **Important note on the SoftwareSerial library**
 *  Not all pins on the Mega and Mega 2560 support change interrupts,
 *  so only the following can be used for RX:
 *  10, 11, 12, 13, 50, 51, 52, 53, 62, 63, 64, 65, 66, 67, 68, 69
 */

// Virtual Serial Port
SoftwareSerial CO2_internal(T66_1_Rx_PIN, T66_1_Tx_PIN);


SoftwareSerial CO2_external(T66_2_Rx_PIN, T66_2_Tx_PIN);


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
const byte CO2_EXT      = 0x07;
const byte CO2_CALIBRATE= 0x08;


const byte DAMPERS_CLOSED  = 0;
const byte DAMPERS_OPEN    = 1;

const byte RED = 0;
const byte WHITE = 1;
const byte BLUE = 2;

// For output:
float temperature = 0.0;
float humidity = 0.0;
float co2_ppm = 0.0;
float co2_ext_ppm = 13.37;
byte LED_red   = 0;
byte LED_white = 0;
byte LED_blue  = 0;

byte error_code = 0; // Default


// State Machine
unsigned long previousMillis = 0;
unsigned long interval = 4000; // 2 seconds between each reading

// Fan Test
unsigned long prevLEDMillis = 0;
unsigned long LEDInterval = 5000;

void setup() {
  analogWrite(FAN_INT_PIN, 0);
  analogWrite(FAN_EXT_PIN, 0);
  
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  
  Serial.begin(RPi_BAUD);         // With Raspberry Pi
  hum_temp_init();                
  CO2_internal.begin(T66_BAUD);     // Opens virtual serial port with the internal CO2 Sensor
  CO2_external.begin(T66_BAUD);     // Opens virtual serial port with the external CO2 Sensor
  
  DamperServos.begin(SERVO_BAUD);

  // for debug
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  unsigned long currentMillis = millis();
  
  listen_for_handshake();

  update_data(currentMillis);  
}

void update_data(unsigned long currentMillis) {
  byte h_t_rsp[TEMP_HUM_RSP_SIZE]; // To hold humidity/temperature readings
  
  if (currentMillis - previousMillis > interval) {
    //digitalWrite(LED_BUILTIN, HIGH);
    hum_temp_reading(HUM_TEMP_ADDRESS, (char*)&h_t_rsp);
    humidity = get_hum_from_reading((char*)&h_t_rsp);
    temperature = get_temp_from_reading((char*)&h_t_rsp);
    co2_ppm = CO2_reading(&CO2_internal, 1000);  // Spend at most 1 second here
    co2_ext_ppm = CO2_reading(&CO2_external, 1000); // Spend at most 1 second here
    previousMillis = currentMillis;
    //digitalWrite(LED_BUILTIN, LOW);
  }
}

void listen_for_handshake() {
  byte header = 0;

  if (Serial.available() > 0) {
    header = Serial.read();    
    validate_and_handle_msg(header);
  }
}

bool ready_for_requests() {
  if (T66_has_status(&CO2_internal, WARM_UP_FLAG)) {
    return false; 
  }
  if (T66_has_status(&CO2_external, WARM_UP_FLAG)) {
    return false;
  }
  return true;
}

void handle_instruction(byte instruction, byte* payload, unsigned int pl_size) {
  
  if (instruction == TEMPERATURE) {
    RPi_send_float(TEMPERATURE, temperature);
    
  } else if (instruction == HUMIDITY) {
    RPi_send_float(HUMIDITY, humidity);
    
  } else if (instruction == CO2) {
    RPi_send_float(CO2, co2_ppm);
    
  } else if (instruction == FAN_INT) {
    if (set_internal_fan_speed(payload, pl_size))
      send_ack(instruction);
    else
      send_error(instruction);
      
  } else if (instruction == FAN_EXT) {
    if (set_external_fan_speed(payload, pl_size))
      send_ack(instruction);
    else
      send_error(instruction);
  } else if (instruction == SERVOS) {
    if (set_servos(payload, pl_size))
      send_ack(instruction);
    else
      send_error(instruction);
      
  } else if (instruction == LED) {
    if (set_LED(payload, pl_size)) 
      send_ack(instruction);
    else 
      send_error(instruction);
  } else if (instruction == CO2_EXT) {
    RPi_send_float(CO2_EXT, co2_ext_ppm);
  } else if (instruction == CO2_CALIBRATE) {
    if (CO2_calibrate(payload, pl_size))
      send_ack(instruction);
    else
      send_error(instruction);
  }
}

void validate_and_handle_msg(byte header) {
  if (!is_valid_header(header)) return;
  
  unsigned int msg_size = get_size(header);

  if (msg_size < 2) return;

  byte* msg = (byte *)malloc(sizeof(byte)*msg_size);

  Serial.readBytes(msg, msg_size);

  if (validate_checksum(msg, msg_size)) {
    byte instruction = msg[0];
    byte *payload = &msg[1];
    unsigned int pl_size = msg_size - 2;
    
    handle_instruction(instruction, payload, pl_size);
  }

  free(msg);
}

bool validate_checksum(byte* payload, unsigned int pl_size) {
  byte cs = 0;

  for (int i=0; i<pl_size-1; i++) { 
    cs += payload[i];
  }

  cs %= 0x100;

  if (payload[pl_size-1] == cs) return true;
  else return false;
}


void send_ack(byte packet)
{
  Serial.write(packet); // Return the instruction packet to signify success
}

void send_error(byte packet)
{
  Serial.write(~packet); // Return a negated instruction to signify an error
  Serial.write(error_code);
  error_code = 0;
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

bool set_internal_fan_speed(byte* payload, unsigned int pl_size) {
  return set_fan_speed(payload, pl_size, FAN_INT_PIN);
}

bool set_external_fan_speed(byte* payload, unsigned int pl_size) {
  return set_fan_speed(payload, pl_size, FAN_EXT_PIN);
}

bool set_fan_speed(byte* payload, unsigned int pl_size, int pin_num) {
  if (pl_size < 1) return false;
  byte spd = payload[0]; // Only use 1 byte
  analogWrite(pin_num, spd);
  return true;
}

bool set_servos(byte* payload, unsigned int pl_size) {
  if (pl_size < 1) return false;

  byte signl = payload[0]; // Signal from the Raspberry Pi. 0: close dampers, 1: open dampers

  if (signl == DAMPERS_OPEN) open_dampers(&DamperServos, LEFT_ADDR, RIGHT_ADDR);
  else if (signl == DAMPERS_CLOSED) close_dampers(&DamperServos, LEFT_ADDR, RIGHT_ADDR);

  return true;
}

bool set_LED(byte* payload, unsigned int pl_size) {
  if (pl_size < 3) return false;

  byte red = payload[0];
  byte white = payload[1];
  byte blue = payload[2];

  analogWrite(LED_RED_PIN, red);
  analogWrite(LED_WHT_PIN, white);
  analogWrite(LED_BLU_PIN, blue);

  return true;
}

bool CO2_calibrate(byte* payload, unsigned int pl_size) {
  // Start calibrating both CO2 sensors at the same time. Wait for the sensors to finish internal calibration
  // before returning true or false, depending on the result.
  if (pl_size != 2)
    return false;

  digitalWrite(LED_BUILTIN, LOW);
  int msb = payload[0];
  int lsb = payload[1];

  int ppm_value = (msb << 8) + lsb;

  // Set target PPM
  if ((!T66_set_calibration_target(&CO2_internal, ppm_value, &error_code)) || (!T66_set_calibration_target(&CO2_external, ppm_value, &error_code))) {
    return false;
  }
  delay(1000);

  digitalWrite(LED_BUILTIN, HIGH);

  // Verify that target was set in sensors
  if ((!T66_verify_calibration_target(&CO2_internal, ppm_value, &error_code)) || (!T66_verify_calibration_target(&CO2_external, ppm_value, &error_code))) {
    return false;
  }
  delay(1000);
  
  // Start calibration
  if ((!T66_start_calibration(&CO2_internal, &error_code)) || (!T66_start_calibration(&CO2_external, &error_code))) {
    return false;
  }
  delay(1000);

  // Wait until both sensors are done calibrating
  while ((T66_has_status(&CO2_internal, CALIBRATION_FLAG)) || (T66_has_status(&CO2_external, CALIBRATION_FLAG))) delay(50);

  digitalWrite(LED_BUILTIN, LOW);

  return true;
}

