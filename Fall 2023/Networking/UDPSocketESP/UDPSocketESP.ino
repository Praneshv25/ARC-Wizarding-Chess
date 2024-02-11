#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "wizardschess";
const char* password = "wizardschess";
unsigned int localPort = 12345;  // same as server
const int STATUS_LED = 2;
const byte deviceId = 3; // Device ID as a byte

int startTime = millis();

WiFiUDP udp;

void setup() {
    pinMode(STATUS_LED, OUTPUT);
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        digitalWrite(STATUS_LED, HIGH);
        delay(250);
        digitalWrite(STATUS_LED, LOW);
        delay(250);
        Serial.println("Connecting to server");
    }

    digitalWrite(STATUS_LED, HIGH);

    udp.begin(localPort);
    sendInitPacket();



    
}

void loop() {


  if (millis() - startTime > 1000) {
    sendInitPacket();
    startTime = millis();
  }

  int packetSize = udp.parsePacket();
  if (packetSize) {
      IPAddress remoteIP = udp.remoteIP(); // Store the sender's IP address
      unsigned int remotePort = udp.remotePort(); // Store the sender's port number

      byte incomingPacket[16] = {0}; // Initialize all elements to zero
      int len = udp.read(incomingPacket, sizeof(incomingPacket));
      if (len > 0) {
        if(incomingPacket[0] == 'W' && incomingPacket[1] == 'I' && incomingPacket[2] == 'Z' ){
          Serial.write(incomingPacket, len);  // Send to Raspberry Pi Pico
          //Serial.println();
          //printByteArray(incomingPacket, len);
        }
          //Start of switch fiddling
         /* switch(incomingPacket[0]){//should be incomingPacket[1] for future uses, soley for testing now
            case 1:
            if(len < 3)
            {
              Serial.println("Error: not enough arguments");
              udp.println("Error: not enough arguments");
              break;
            }
            move(incomingPacket[1],incomingPacket[2]);
            break;
            case 2:
            break;
            case 3:
            break;
            default:
            Serial.println("Command not recognized");
            break;
          }
        } 


          //end of switch fiddling
*/
          // Echo back to sender as acknowledgement
          udp.beginPacket(remoteIP, remotePort);
          udp.write(incomingPacket, len);
          udp.endPacket();
      }
  
  }
  // Check if the Pico has sent any data over Serial to forward
  if (Serial.available()) {
      byte outgoingPacket[16] = {0}; // Buffer to store data from Pico
      size_t len = Serial.readBytes(outgoingPacket, sizeof(outgoingPacket));

      // Echo back to sender
      IPAddress remoteIP = udp.remoteIP();
      unsigned int remotePort = udp.remotePort();
      udp.beginPacket(remoteIP, remotePort);
      udp.write(outgoingPacket, len);
      udp.endPacket();
  }
}

void sendInitPacket() {
  // Send a "hello" message with the unique device ID
    byte initPacket[] = {0xAA, deviceId, deviceId}; // Init packet
    udp.beginPacket(IPAddress(255, 255, 255, 255), localPort); // Broadcasting
    udp.write(initPacket, sizeof(initPacket));
    udp.endPacket();
    //Serial.println("Broadcasted init packet");
}

void printByteArray(const byte* array, size_t length) {
  //Serial.print(array[0]);
  //Serial.println(" is the first byte in the array");
    for (size_t i = 0; i < length; i++) {
        if (array[i] < 0x10) {
            Serial.print("0"); // Print leading zero for single digit hex values
        }
        Serial.print(array[i], HEX); // Print byte in HEX
        Serial.print(" "); // Add a space between bytes for readability
    }
    Serial.println(); // New line after printing the array
}

void move(int speed, int direction)
{
  Serial.print("moving at speed: ");
  Serial.println(speed);
  
  if(direction == 1)
  {
    Serial.println("Forward");
    
  }
  else
  {
    Serial.println("Backward");
    
  }
}
