//To program the Pico:
//    1) Press and hold the Pico's BOOTSEL button
//    2) Plug pico into USB port
//    3) Release the Pico's BOOTSEL button
//    4) Click on the Arduino IDE => button to program

//The RX pin from the ESP01 goes to the TX pin on the pico and vice versa
#include <pio_encoder.h>
const int BUTTON_PIN = 28;
const int TX_PIN = 0;
const int RX_PIN = 1;
bool blinkyFlag = false;


const int motor1a = 18;
const int motor1b = 17;
const int l293Enable = 16;
const int motor2a = 13;
const int motor2b = 14;
const int l2932Enable = 15;
const int encoderA = 10;
const int encoder2A = 20;

PioEncoder motor0(encoderA);
PioEncoder motor1(encoder2A);
long encoderCounts = -999;
long newEncoderCounts;
int speed = 255;


void setup() {
    Serial.begin(115200);

    Serial1.setRX(RX_PIN);
    Serial1.setTX(TX_PIN);
    Serial1.begin(115200);
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT);
    pinMode(motor1a, OUTPUT);
    pinMode(motor1b, OUTPUT);
    pinMode(l293Enable, OUTPUT);
    pinMode(motor2a, OUTPUT);
    pinMode(motor2b, OUTPUT);
    pinMode(l2932Enable, OUTPUT);
    digitalWrite(l293Enable, HIGH);
    digitalWrite(l2932Enable, HIGH);
    digitalWrite(LED_BUILTIN, HIGH);
    motor0.begin();
    motor0.reset();
    motor1.begin();
    motor1.reset();
    digitalWrite(LED_BUILTIN, HIGH);
    
}

void loop() {
  //Serial.println("Seeing if there is data to read ");
  //Serial.println(Serial1.available());
    if(Serial1.available()) {
        byte incomingPacket[16] = {0}; //Format [command direction speed]
        int len = Serial1.readBytes(incomingPacket, sizeof(incomingPacket));
        //Serial.println(len);
        /*if(incomingPacket[0] == 'W' && incomingPacket[1] == 'I' && incomingPacket[2] == 'Z' ) //if the incoming packet contains the password as the first 3 index of array, then process the command
        { //Filter did not work, might have to filter from the ESP side
          Serial.println("Running Command");
          
        }*/
        Serial.print(incomingPacket[3]);
        Serial.print(" ");
        Serial.print(incomingPacket[4]);
        Serial.print(" ");
        Serial.print(incomingPacket[5]);
        Serial.println(" ");

        char response = process_command(incomingPacket);
        Serial1.write(response);
    }
    if(blinkyFlag) {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(500);
      digitalWrite(LED_BUILTIN, LOW);
      delay(500);
    }
}

char process_command(byte packet[16]) {
    switch(packet[3]){
      case 1:
        if(packet[4] == 1) //backward
        {
          digitalWrite(motor1a, LOW);
          analogWrite(motor1b, packet[5]);
          digitalWrite(motor2a, LOW);
          analogWrite(motor2b, packet[5]);
          Serial.println("backward");
          
        }
        else //forward
        {
          analogWrite(motor1a, packet[5]);
          digitalWrite(motor1b, LOW);
          analogWrite(motor2a, packet[5]);
          digitalWrite(motor2b, LOW);
          Serial.println("forward");
        }
        return 'M';
      case 2:
        if(packet[4] == 1) //clockwise
        {
          analogWrite(motor1a, packet[5]);
          digitalWrite(motor1b, LOW);
          digitalWrite(motor2a, LOW);
          analogWrite(motor2b, packet[5]);
        }
        else //counter clockwise
        {
          digitalWrite(motor1a, LOW);
          analogWrite(motor1b, packet[5]);
          analogWrite(motor2a, packet[5]);
          digitalWrite(motor2b, LOW);
        }
        return 'T';
      case 3:
        digitalWrite(motor1a, LOW);
        digitalWrite(motor1b, LOW);
        digitalWrite(motor2a, LOW);
        digitalWrite(motor2b, LOW);
        Serial.println("Stop");
        return 'S';
      default:
        return 'E';
    }
    
    
    
    
    
}  
    /*if (command == '1') {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(500);
        digitalWrite(LED_BUILTIN, LOW);
        delay(500);

            analogWrite(motor1a, speed);
            digitalWrite(motor1b, LOW);
            analogWrite(motor2a, speed);
            digitalWrite(motor2b, LOW);
        return 'F';  // Acknowledge receipt and execution of command 1
    }
    else if (command == '2') {
        //Serial.println("Command 2: Backward");
            digitalWrite(motor1a, LOW);
            analogWrite(motor1b, speed);
            digitalWrite(motor2a, LOW);
            analogWrite(motor2b, speed);
            return 'B';
    }
    else if (command == '3') {
      //Serial.println("Command 3: Stop");
            digitalWrite(motor1a, LOW);
            digitalWrite(motor1b, LOW);
            digitalWrite(motor2a, LOW);
            digitalWrite(motor2b, LOW);
            return 'S';
    }
    else if (command == '4') {
      return 'h';
    }
    else {
        return 'E';  // Unrecognized command, sending back error signal
    }
    */

