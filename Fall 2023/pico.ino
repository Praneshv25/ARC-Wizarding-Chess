int buttonPin = 28;

void setup() {
    Serial.begin(115200);
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(buttonPin, INPUT);
}

void loop() {
    if(Serial.available()) {
        char command = Serial.read();
        char response = process_command(command);
        Serial.write(response);
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
        int pinState = digitalRead(buttonPin);
        return pinState ? 'H' : 'L';  // Send back pin state, 'H' for HIGH and 'L' for LOW
    }
    else {
        return 'E';  // Unrecognized command, sending back error signal
    }
}
