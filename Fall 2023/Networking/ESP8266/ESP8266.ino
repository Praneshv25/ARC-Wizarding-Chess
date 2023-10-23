// To program the ESP8266:
//    1) Plug ESP8266 into programmer
//    2) Plug programmer into USB port
//    3) Press the ESP8266's program button which is on the programmer
//    4) Click on the Arduino IDE => button to program

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "wizardschess";
const char* password = "wizardschess";
unsigned int localPort = 12345;  // same as server
const int STATUS_LED = 2;
String deviceId = "ESP1";

WiFiUDP udp;


void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        // digitalWrite(STATUS_LED, HIGH);
        // delay(250);
        // digitalWrite(STATUS_LED, LOW);
        // delay(250);
        Serial.println("Connecting to server");
        delay(1000);
    }

    digitalWrite(STATUS_LED, HIGH);

    udp.begin(localPort);

    // Send a "hello" message with the unique device ID
    udp.beginPacket("192.168.2.2", localPort);
    udp.write(("INIT:" + deviceId).c_str());
    udp.endPacket();
    Serial.println("Sent init packet");
}

void loop() {
    int packetSize = udp.parsePacket();
    if (packetSize) {
        char incomingPacket[16];
        int len = udp.read(incomingPacket, 16);
        if (len > 0) {
            incomingPacket[len] = 0; // Null-terminate
        }
        Serial.write(incomingPacket, len);  // Send to Raspberry Pi Pico
    }

    if (Serial.available()) {
      String dataFromPico = Serial.readString();
      udp.beginPacket(udp.remoteIP(), udp.remotePort());
      udp.write(dataFromPico.c_str());
      udp.endPacket();
  }
}
