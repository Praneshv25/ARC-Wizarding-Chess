// A Small example to run the pico motors with the serial monitor
#include <pio_encoder.h>
const int motor1a = 18;
const int motor1b = 16;
const int l293Enable = 19;
const int motor2a = 13;
const int motor2b = 14;
const int l2932Enable = 15;
const int encoderA = 10;
const int encoder2A = 20;

float oneTurn = 4800; // num of encoder counts for one full turn
long wheelDist = 5; // distance between the wheels in [UNITS]
float radius = 43; // for angle calculations later (same as wheelDist for them)
float arcLength;
float pi = 3.14159;
float wheelCirc = 2 * radius * pi; // wheel circumference
float numRotate; // how many times the wheel needs to rotate for the desired angle/outcome in terms of # encoder counts
long encoderCountsA = 0;
long encoderCountsB = 0;

PioEncoder motor0(encoderA);
PioEncoder motor1(encoder2A);
long encoderCounts = -999;
long newEncoderCounts;
int speed = 255;


void setup() {
    // put your setup code here, to run once:
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(motor1a, OUTPUT);
    pinMode(motor1b, OUTPUT);
    pinMode(l293Enable, OUTPUT);
    pinMode(motor2a, OUTPUT);
    pinMode(motor2b, OUTPUT);
    pinMode(l2932Enable, OUTPUT);
    digitalWrite(l293Enable, HIGH);
    digitalWrite(l2932Enable, HIGH);
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.begin(115200);
    motor0.begin();
    motor0.reset();
    motor1.begin();
    motor1.reset();


}

void loop() {
    Serial.println("Enter a command: ");
    Serial.println("1: Forward");
    Serial.println("2: Backward");
    Serial.println("3: Stop");
    Serial.println("4: Reset Encoder");
    Serial.println("5: Read Encoder");
    Serial.println("6: Move for 1 second");
    Serial.println("7: Move for 1000 counts");
    // Read in from the serial monitor
    while(Serial.available() == 0) {
        // Do nothing, wait for serial input
    }
    int command = Serial.parseInt();

    // Execute the command
    switch (command) {
        case 1:
            Serial.println("Command 1: Forward");
            analogWrite(motor1a, speed);
            digitalWrite(motor1b, LOW);
            analogWrite(motor2a, speed);
            digitalWrite(motor2b, LOW);
            break;
        case 2:
            Serial.println("Command 2: Backward");
            digitalWrite(motor1a, LOW);
            analogWrite(motor1b, speed);
            digitalWrite(motor2a, LOW);
            analogWrite(motor2b, speed);
            break;

        case 3:
            Serial.println("Command 3: Stop");
            digitalWrite(motor1a, LOW);
            digitalWrite(motor1b, LOW);
            digitalWrite(motor2a, LOW);
            digitalWrite(motor2b, LOW);
            break;

        case 4:
            Serial.println("Command 4: Reset Encoder");
            motor0.reset();
            motor1.reset();
            break;

        case 5:
            Serial.println("Command 5: Read Encoder");
            Serial.print("Motor A Encoder Value:");
            Serial.println(motor0.getCount());
            Serial.print("Motor B Encoder Value:");
            Serial.println(motor1.getCount());
            break;

        case 6:
            angleTurn(1,45);
            break;

        case 7:
            Serial.println("Command 7: Move for 1000 counts");
            encoderCounts = motor0.getCount();
            newEncoderCounts = encoderCounts + 1000;
            while (encoderCounts < newEncoderCounts) {
                analogWrite(motor1a, speed);
                digitalWrite(motor1b, LOW);
                encoderCounts = motor0.getCount();
            }
            digitalWrite(motor1a, LOW);
            digitalWrite(motor1b, LOW);
            break;
        case 8:
            Serial.println("Command 8: Set Speed (Input a number between 0 and 255)");
            Serial.println(Serial.available());
            speed = Serial.parseInt();
            delay(1000);
            break;

        default:
            Serial.println("Command not recognized");
            break;
    }
}


void angleTurn(int direction, float angle) //assume direction = 0 is CW and direction = 1 is CCW
{
  //reset encoders
  motor0.reset();
  motor1.reset();
  //calculates number of counts needed to turn a given angle
  arcLength = angle * (pi / 180.00) * wheelDist * 25.4;
  arcLength = arcLength / wheelCirc; // gets # wheel circumferences necessary
  numRotate = arcLength * oneTurn; //number of counts to rotate


  //set the motors to turn the correct direction
  analogWrite(motor1a, (direction*speed));
  analogWrite(motor1b, ((1-direction)*speed));
  analogWrite(motor2a, ((1-direction)*speed));
  analogWrite(motor2b, (direction*speed));
    

  while((encoderCountsA < numRotate) && (encoderCountsB < numRotate))
  {            
    encoderCountsA = motor0.getCount();
    encoderCountsB = motor1.getCount();
  }

  //Set everything to 0
  analogWrite(motor1a, 0);
  digitalWrite(motor1b, LOW);
  analogWrite(motor2b, 0);
  digitalWrite(motor2a, LOW);
  
  encoderCountsA = 0;
  encoderCountsB = 0;
}