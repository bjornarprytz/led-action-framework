#include "Arduino.h"
#include "T66CO2.h"

bool T66_has_status(SoftwareSerial *com, int status_flag) {
  if (sensor_status(com, 40) & status_flag) {
    return true;
  } else {
    return false;
  }
}

bool set_elevation(SoftwareSerial *com, int elevation, byte *error_code) {
  byte lsb = elevation % 0x100; // 256
  byte msb = elevation >> 8;

  byte command[] = {0xFF, 0xFE, 0x03, 0x0F, msb, lsb};
  byte response[] = {1,1,1};
  int rsp_size = 3;

  if (!T66_sendCommand(com, command, response, rsp_size, error_code))
    return false;

  return T66_validate_ack(response, rsp_size, error_code);
}

bool T66_ABC_logic_off(SoftwareSerial *com, byte *error_code) {
  byte abc_status[] = {0xFF, 0xFE, 0x02, 0xB7, 0x00};
  byte response[] = {0,0,0,0};
  int rsp_size = 4;

  // Check whether ABC logic is already off
  if(!T66_sendCommand(com, abc_status, response, rsp_size, error_code)) return false;
  if (response[rsp_size-1] == ABC_LOGIC_OFF) return true;

  byte abc_off[] = {0xFF, 0xFE, 0x02, 0xB7, ABC_LOGIC_OFF};

  // Turn ABC logic off if necessary
  if(!T66_sendCommand(com, abc_off, response, rsp_size, error_code)) return false;
  if (response[rsp_size-1] == ABC_LOGIC_OFF) return true;
  else {
    *error_code = CO2_ABC_BAD_ACK;
    return false;
  }
}

bool T66_set_calibration_target(SoftwareSerial *com, int ppm_value, byte *error_code) {
  // Send a calibration signal to the sensor.
  byte lsb = ppm_value % 0x100; // 0x--XX
  byte msb = ppm_value >> 8;    // 0xXX--

  byte command[] = {0xFF, 0xFE, 0x04, 0x03, 0x11, msb, lsb};
  byte response[] = {1,1,1};

  int rsp_size = 3;

  if (!T66_sendCommand(com, command, response, rsp_size, error_code))
    return false;

  delay(30);

  // Validate the response
  return T66_validate_ack(response, rsp_size, error_code);
}

bool T66_verify_calibration_target(SoftwareSerial *com, int ppm_value, byte *error_code) {
  byte command[] = {0xFF, 0xFE, 0x02, 0x02, 0x11};
  byte response[] = {0,0,0,0,0};
  int rsp_size = 5;

  if (!T66_sendCommand(com, command, response, rsp_size, error_code))
    return false;

  int msb = response[3];
  int lsb = response[4];

  int sensor_calibration_ppm = (msb << 8) + lsb;
  if (ppm_value == sensor_calibration_ppm)
    return true;
  else
    return false;
}

bool T66_start_calibration(SoftwareSerial *com, byte *error_code) {
  byte startCalibration[] = {0xFF, 0xFE, 0x01, 0x9B};
  byte response[] = {1,1,1};
  int rsp_size = 3;

  if (!T66_sendCommand(com, startCalibration, response, rsp_size, error_code))
    return false;

  return T66_validate_ack(response, rsp_size, error_code);
}

bool T66_validate_ack(byte response[], int rsp_size, byte *error_code) {
  if (response[rsp_size-1] == 0x00) { // Validate the ACK
    return true;
  }
  *error_code = 0x0;
  return false;
}

bool start_warmup(SoftwareSerial *com, byte *error_code) {
  byte command[] = {0xFF, 0xFE, 0x01, 0x84};
  byte* response;

  int rsp_size = 0;
  T66_sendCommand(com, command, response, rsp_size, error_code);
}

byte sensor_status(SoftwareSerial *com, byte *error_code) {
  byte readStatus[] = {0xFF, 0xFE, 0x01, 0xB6}; // Read status byte
  byte response[] = {0,0,0,0}; // 4 byte array to hold the response
  int rsp_size = 4;
  T66_sendCommand(com, readStatus, response, rsp_size, error_code);
  return response[rsp_size-1];
}

float CO2_reading(SoftwareSerial *com, byte *error_code) {

  byte readCO2[] = {0xFF, 0xFE, 0x02, 0x02, 0x03}; // Read co2 command
  byte response[] = {0,0,0,0,0}; // 5 byte array to hold the response
  int rsp_size = 5;

  T66_sendCommand(com, readCO2, response, rsp_size, error_code);

  return (float)T66_getValue(response);
}

unsigned long T66_getValue(byte packet[]) {
  // by Marv kausch @ Co2meter.com
  int high = packet[3]; //high byte for value is 4th byte in packet in the packet
  int low = packet[4]; //low byte for value is 5th byte in the packet
  unsigned long val = high*256 + low; //Combine high byte and low byte with this formula to get value
  return val;
}

bool T66_sendCommand(SoftwareSerial *com, byte command[], byte response[], int rsp_size, byte *error_code) {
  // based on code from Marv kausch @ Co2meter.com
  com->listen(); // In case there are several devices connected via SoftwareSerial, activate this one

  int cmd_size = command[2] + 3;
  int tries = 3;

  do {
    if (tries <= 0) {
      *error_code = CO2_NO_RESPONSE;
      return false;
    }
    com->write(command,cmd_size);
    if (rsp_size < 1) return true; // Don't wait for a response unless we expect to get one.

    tries--;

    delay(500);
  } while (!com->available());

  return T66_get_response(com, response, rsp_size, error_code);
}

bool T66_get_response(SoftwareSerial *com, byte response[], int rsp_size, byte *error_code) {
  if (!com->isListening()) {
    *error_code = CO2_NOT_LISTENING;
    return false;
  }
  int timeout=10;
  while(com->available() < rsp_size ) { //Wait to get a full response
    timeout--;
    if(timeout <= 0) {
      while(com->available()) com->read();  // Flush whatever we have, in case of a timeout

      *error_code = CO2_TIMEOUT;
      return false;
    }
    delay(30);
  }

  for (int i=0; i < rsp_size; i++)
    response[i] = com->read();
  return true;
}
