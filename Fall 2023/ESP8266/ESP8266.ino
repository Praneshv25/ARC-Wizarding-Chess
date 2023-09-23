#include <ESP8266WiFi.h>

const char* ssid = "wizardschess";
const char* password = "wizardschess";
const char* serverIP = "192.168.2.2";
const uint16_t serverPort = 1234;
const int STATUS_LED = 0;

WiFiClient client;

void setup() {
    Serial.begin(115200);
    pinMode(STATUS_LED, OUTPUT);
    digitalWrite(STATUS_LED, LOW);

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
//        Serial.print(".");
    }

    client.connect(serverIP, serverPort);
    client.print("ESP2");  // Change to a unique identifier for each ESP-Pico pair
}

void loop() {
  int time = millis();

  if (!client.connected()) {
    digitalWrite(STATUS_LED, LOW);
    // If not connected, try to reconnect
    if (!client.connect(serverIP, serverPort)) {
      Serial.println("Conneting to server");
      delay(5000);  // Wait before trying again
    } else {
      // Once connected, send the device ID to the server
      client.println("ESP2");  // Replace with your actual device ID
    }
  } else {
    digitalWrite(STATUS_LED, HIGH);
  }

  // If there is data from the Pico, send it to the server
  if (Serial.available()) {
      String dataFromPico = Serial.readString();
      client.print(dataFromPico);
  }

  // If there is data from the server, send it to the Pico
  if (client.available()) {
      String dataFromServer = client.readString();
      Serial.print(dataFromServer);
  }

}
