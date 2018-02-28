/*                          AN-157 Demo of T-66 using Software Serial

 Arduino example for t6613 CO2 sensor 0-2000 PPM   19200 BPS
 2/2017 by Marv kausch @ Co2meter.com
*/
#include "SoftwareSerial.h"
SoftwareSerial T66_Serial(12,13); //Sets up a virtual serial port
 //Using pin 12 for Rx and pin 13 for Tx
byte readCO2[] = {0xFF, 0XFE,2,2,3}; //T66 read CO2 command: 5 bytes

byte response[] = {0,0,0,0,0}; //create an array to store the response


void setup()
{
 // put your setup code here, to run once:
 Serial.begin(9600); //Opens the main serial port to communicate with the computer
 T66_Serial.begin(19200); //Opens the virtual serial port with a baud of 9600
 Serial.println("    Demo of AN-157  Software Serial and T66 sensor");
 Serial.print("\n");
}

void loop()
{
 sendRequest(readCO2);   //Locate the problem of program reset whduring this function call
 
 unsigned long valCO2 = getValue(response);// Request from sensor 5 bytes of data
 Serial.print("Sensor response:   ");
 for(int i=0;i<5;i++)
 {
  Serial.print(response[i],HEX);
  Serial.print(" ");
 }
 Serial.print("    Co2 ppm = ");
 Serial.println(valCO2);
delay(2000);  //T6613 spec indicates signal update every 4 seconds
}

void sendRequest(byte packet[])
{
 while(!T66_Serial.available()) //keep sending request until we start to get a response
 {
   T66_Serial.write(readCO2,5);// Write to sensor 5 byte command
   delay(50);
   delay(1000);
 }
 int timeout=0; //set a timeoute counter
 while(T66_Serial.available() < 5 ) //Wait to get a 7 byte response
 {
   timeout++;
   if(timeout > 10) //if it takes too long there was probably an error
   {
    Serial.print("Timeout");
   
    while(T66_Serial.available()) //flush whatever we have
      T66_Serial.read();
      
    break; //exit and try again
   }
 delay(50);
 }
  for (int i=0; i < 5; i++) response[i] = T66_Serial.read();
}

unsigned long getValue(byte packet[])
{
 int high = packet[3]; //high byte for value is 4th byte in packet in the packet
 int low = packet[4]; //low byte for value is 5th byte in the packet
 unsigned long val = high*256 + low; //Combine high byte and low byte with this formula to get value
 return val;
}
