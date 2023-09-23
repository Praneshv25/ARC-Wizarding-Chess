const int BUTTON_PIN = 28;
const int TX_PIN = 0;
const int RX_PIN = 1;
bool blinkyFlag = false;


void setup() {
    Serial.begin(115200);

    Serial1.setRX(RX_PIN);
    Serial1.setTX(TX_PIN);
    Serial1.begin(115200);
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT);
    digitalWrite(LED_BUILTIN, HIGH);
    
}

void loop() {
    if(Serial1.available()) {
        char command = Serial1.read();
        char response = process_command(command);
        Serial.print(command);
        Serial1.write(response);
    }
    if(blinkyFlag) {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(500);
      digitalWrite(LED_BUILTIN, LOW);
      delay(500);
    }
}

char process_command(char command) {
    if (command == '1') {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(500);
        digitalWrite(LED_BUILTIN, LOW);
        delay(500);
        return 'A';  // Acknowledge receipt and execution of command 1
    }
    else if (command == '2') {
        int pinState = digitalRead(BUTTON_PIN);
        return pinState ? 'H' : 'L';  // Send back pin state, 'H' for HIGH and 'L' for LOW
    }
    else if (command == '3') {
      blinkyFlag = !blinkyFlag;
      return 'B';
    }
    else {
        return 'E';  // Unrecognized command, sending back error signal
    }
}
