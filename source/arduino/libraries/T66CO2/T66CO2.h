#ifndef T66O2_h
#define T66O2_h

#include "Arduino.h"
#include "SoftwareSerial.h"

// T6613 Telaire(CO2) Communication
#define T66_BAUD 19200
#define WARM_UP_FLAG 0x02
#define CALIBRATION_FLAG 0x03

#define CO2_NO_RESPONSE 0xFE
#define CO2_TIMEOUT 0xFD
#define CO2_NOT_LISTENING 0xFC
#define CO2_ABC_BAD_ACK 0xFB

#define ABC_LOGIC_ON 0x01
#define ABC_LOGIC_OFF 0x02


// If the sensor is warming up, it should not be used yet
bool T66_has_status(SoftwareSerial *com, int status_flag);
// Set the elevation level of the sensor. Factors into ppm calculations
bool set_elevation(SoftwareSerial *com, int value, byte *error_code);
// Turn off the Automatic Background Calibration as it interferes with the .
bool T66_ABC_logic_off(SoftwareSerial *com, byte *error_code);
// Set the calibration target. T66_start_calibration must be called to start the actual calibration.
bool T66_set_calibration_target(SoftwareSerial *com, int ppm_value, byte *error_code);
// Verify that the calibration target is the expected value
bool T66_verify_calibration_target(SoftwareSerial *com, int ppm_value, byte *error_code);
// Start the internal calibration routine of the sensor. Call ONLY AFTER setting calibration target (verification of calibration target is also recommended)
bool T66_start_calibration(SoftwareSerial *com, byte *error_code);
// Validate the response as an ACK
bool T66_validate_ack(byte response[], int rsp_size, byte *error_code);
// Resets the sensor and starts the warmup sequence
bool start_warmup(SoftwareSerial *com, byte *error_code);
// Get a byte which includes the various status flags in the T6613 Telaire sensor
byte sensor_status(SoftwareSerial *com, byte *error_code);
// Top level function that tries the sensor for [grace] amount of milliseconds
float CO2_reading(SoftwareSerial *com, byte *error_code);
// Sends a request over the SoftwareSerial interface and stores the response in the input buffer
bool T66_sendCommand(SoftwareSerial *com, byte command[], byte response[], int rsp_size, byte *error_code);
// Extracts the CO2 ppm from the input packet.
unsigned long T66_getValue(byte packet[]);
// Get a response from the sensor after determining that it has responded
bool T66_get_response(SoftwareSerial *com, byte response[], int rsp_size, byte *error_code);


#endif
