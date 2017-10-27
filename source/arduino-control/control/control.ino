// By Bjørnar Prytz


const byte CONTROL_MASK = B10000000;

const byte TEMPERATURE  = B0000000;
const byte HUMIDITY     = B0000001;
const byte CO2          = B0000010;
const byte FAN_SPEED    = B0000011;
const byte SERVOS       = B0000100;
const byte LED_RED      = B0000101;
const byte LED_WHT      = B0000110;
const byte LED_BLU      = B0000111;

const byte RSP_TMP      = B00000000;
const byte RSP_HUM      = B01000000;
const byte RSP_CO2      = B10000000;

const byte RED = 0;
const byte WHITE = 1;
const byte BLUE = 2;

float temperature = 14.24512;
float humidity = 61.14214;
float co2_ppm = 12.23;

// For debugging:
byte fan_speed = 0;
byte servo_pos = 0;
byte LED_red   = 0;
byte LED_white = 0;
byte LED_blue  = 0;

bool wait_and_listen(unsigned int patience) {
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

void setup() {
  Serial.begin(9600);  // start serial communication

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);

  // Warmup CO2 sensor (start a timer?)
}

void loop() {
  byte packet = 0;
  digitalWrite(LED_BUILTIN, LOW);
  if (Serial.available() > 0) {
    digitalWrite(LED_BUILTIN, HIGH);
    packet = Serial.read();
    
    if (is_instruction(packet)) {
      packet %= 0x80;             // Remove the instruction bit
      handle_instruction(packet); // and handle the instruction
    
    } else {
      Serial.println("got an unexpected non-instruction");
    }
  }
}

void handle_instruction(byte packet) {
  if (packet == TEMPERATURE) {
    get_temperature();
  } else if (packet == HUMIDITY) {
    get_humidity();
  } else if (packet == CO2) {
    get_co2();
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

void send_data(byte type, byte data) {
  Serial.write(type);
  Serial.write(data);
}

void send_float(byte type, float data) {
  String buf = String(data);
  Serial.write(type);
  Serial.println(buf);
}

void get_temperature() {
  byte data = byte(temperature);
  send_float(RSP_TMP, temperature);
}

void get_humidity() {
  byte data = byte(humidity);
  send_float(RSP_HUM, humidity);
}

void get_co2() {
  byte data = co2_ppm;
  send_float(RSP_CO2, co2_ppm);
}

void set_fan_speed() {
  byte packet;

  if (wait_and_listen(10)) { // Wait 1 second for follow-up data
    packet = Serial.read();
    if (is_data(packet)) {
      fan_speed = packet; // TODO: signal actuator
    }
  }
}

void set_servos() {
  byte packet;
  
  if (wait_and_listen(10)) { // Wait 1 second for follow-up data
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
      if (wait_and_listen(10)) { // Wait 1 second for follow-up data
        packet = Serial.read();
        if (is_data(packet)) {
          LED_red = packet; // TODO: signal actuator
        }
      }
      break;
    case WHITE:
      if (wait_and_listen(10)) { // Wait 1 second for follow-up data
        packet = Serial.read();
        if (is_data(packet)) {
          LED_white = packet; // TODO: signal actuator
        }
      }
      break;
    case BLUE:
      if (wait_and_listen(10)) { // Wait 1 second for follow-up data
        packet = Serial.read();
        if (is_data(packet)) {
          LED_blue = packet; // TODO: signal actuator
        }
      }
      break;
  }
}
