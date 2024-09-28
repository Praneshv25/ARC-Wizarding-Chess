//To program the Pico:
//    1) Press and hold the Pico's BOOTSEL button
//    2) Plug pico into USB port
//    3) Release the Pico's BOOTSEL button
//    4) Click on the Arduino IDE => button to program

//The RX pin from the ESP01 goes to the TX pin on the pico and vice versa
#include <pio_encoder.h>
// #include <PID_v1.h>

const int BUTTON_PIN = 28;
const int TX_PIN = 0;
const int RX_PIN = 1;
bool blinkyFlag = false;


const int motor1a = 18;
const int motor1b = 16;
const int l293Enable = 19;
const int motor2a = 13;
const int motor2b = 14;
const int l2932Enable = 15;
const int encoderA = 10;
const int encoder2A = 20;
int currentCommand[4] = {0};

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
double encoderCounts = -999;
double goal = 0;
double newEncoderCounts;
int maxSpeed = 200;
double speed = 200;
int len = 0;

// double Kp = .001, Ki = 0, Kd = 0;
// PID movePID(&speed, &encoderCounts, &goal, Kp, Ki, Kd, DIRECT);


//max number sending bytes is 255, look into how this will affect control, send multiple forward commands? Determine max distance one forward command can go and the scale 


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

    // movePID.SetMode(AUTOMATIC);
    // movePID.SetOutputLimits(0, (double) maxSpeed);    
}

void loop() {
  static byte incomingPacket[128] = {0};
  static int dataIndex = 3;
  //Serial.println("Seeing if there is data to read ");
  //Serial.println(Serial1.available());
    if(Serial1.available()) {
        memset(incomingPacket,0,sizeof(incomingPacket)); //sets all values of array to 0 Format [command direction speed]
        len = Serial1.readBytes(incomingPacket, sizeof(incomingPacket));
        dataIndex = 3;
        //Serial.println(len);
        //index 0 - 2 of incoming packet are password, everything else is a command
        // create an array that holds one command at a time and run through all the commands of the incoming packet
        // if a command is ever 0, that means that there are no more commands in the array
       
       for(int j = 0; j < len; j++)
       {
        Serial.println((int)incomingPacket[j]);
       }




       /* Serial.print(incomingPacket[3]);
        Serial.print(" ");
        Serial.print(incomingPacket[4]);
        Serial.print(" ");
        Serial.print(incomingPacket[5]);
        Serial.println(" ");

        char response = process_command(incomingPacket);
        Serial1.write(response);*/
    }
    if((int)incomingPacket[dataIndex] != 0)
    {
      
      Serial.println(dataIndex);
      for(int i = 0; i < 4; i++)\
      {
        currentCommand[i] = (int)incomingPacket[dataIndex++];
      }
      Serial.println(currentCommand[0]);
      Serial.print("\n");


      if(dataIndex == len || (int)incomingPacket[dataIndex] == 0) //if data index at max value or no more commands in array
      {
        dataIndex = 3; //reset data index to start
        memset(incomingPacket,0,sizeof(incomingPacket)); //set data in the old data packet to 0
      } 


      char response = process_command(currentCommand);
      Serial1.write(response);
    }
}
//90degree turn is roughly 3100 encoder counts
//packet[1] == 0 = forward, packet[1] == 1 = backward

char process_command(int packet[4]) {
    switch(packet[0]){
      case 1: //Move forward or backward
          move(packet[1],packet[2],packet[3]);
          stop();
          delay(100);
        return 'M';
      case 2: //Turn
        angleTurn(packet[1],packet[2]);
        stop();
        delay(100);
        return 'T';
      case 3: //Stop
        stop();
        Serial.println("Stop");
        delay(packet[2]*10);
        return 'S';
        
      case 4:
        Serial.print("Motor 0 count:");
        Serial.println(motor0.getCount());
        Serial.print("Motor 1 count:");
        Serial.println(motor1.getCount());
      default:
        return 'E';
    }
}
    
void move(int dir, int counts1, int counts2)
{
  motor0.reset();
  motor1.reset();
  encoderCounts = motor0.getCount();
  double startCounts = encoderCounts;
  double countsToMove = (counts1 * 256 + counts2) * 100;
  goal = startCounts + countsToMove;
  double progress = 0; 
  while(abs(encoderCounts) < goal)
  {
    encoderCounts = motor0.getCount();
    progress = (encoderCounts - startCounts) / (goal - startCounts);

    speed = maxSpeed * move_profile(.25, .1, .9, progress);
    analogWrite(motor1a, ((1-dir)*speed));
    analogWrite(motor1b, (dir*speed));
    analogWrite(motor2a, ((1-dir)*speed));
    analogWrite(motor2b, (dir*speed));
  }
}

void angleTurn(int direction, float angle) //assume direction = 1 is CW and direction = 0 is CCW
{
  //reset encoders
  motor0.reset();
  motor1.reset();
  //calculates number of counts needed to turn a given angle
  arcLength = angle * (pi / 180.00) * wheelDist * 25.4;
  arcLength = arcLength / wheelCirc; // gets # wheel circumferences necessary
  numRotate = arcLength * oneTurn; //number of counts to rotate
  double progress;
  Serial.println("Target: ");
  Serial.println(numRotate);

  while((abs(encoderCountsA) < numRotate) && (abs(encoderCountsB) < numRotate))
  {            
    encoderCountsA = motor0.getCount();
    encoderCountsB = motor1.getCount();

    progress = abs(encoderCountsA) / numRotate;
    speed = maxSpeed * move_profile(.25, .25, .75, progress);

    analogWrite(motor1a, (direction*speed));
    analogWrite(motor1b, ((1-direction)*speed));
    analogWrite(motor2a, ((1-direction)*speed));
    analogWrite(motor2b, (direction*speed));
  }

  Serial.println("Encoder A");
  Serial.println(encoderCountsA);
  Serial.println("Encoder B");
  Serial.println(encoderCountsB);

  //Set everything to 0
  analogWrite(motor1a, 0);
  digitalWrite(motor1b, LOW);
  analogWrite(motor2b, 0);
  digitalWrite(motor2a, LOW);
  
  encoderCountsA = 0;
  encoderCountsB = 0;
}

void stop()
{
  digitalWrite(motor1a, LOW);
  digitalWrite(motor1b, LOW);
  digitalWrite(motor2a, LOW);
  digitalWrite(motor2b, LOW);
  delay(100);
}

double move_profile(double min_speed, double max_1, double max_2, double x) {
  double speed;
  if (x < max_1) {
    speed = min_speed + (x / max_1) * (1 - min_speed);
  } else if (x < max_2) {
    speed = 1;
  } else {
    speed = min_speed + ((1 - x) / (1 - max_2)) * (1 - min_speed);
  }
  return speed > min_speed ? speed : min_speed;
}
/*
Legacy code:

Turning:
          motor0.reset();
          motor1.reset();
          //packet[1] == 0 = CCW, packet[1] == 1 = CW
          analogWrite(motor1a, (packet[1]*speed));
          analogWrite(motor1b, ((1-packet[1])*speed));
          analogWrite(motor2a, ((1-packet[1])*speed));
          analogWrite(motor2b, (packet[1]*speed));
          encoderCounts = motor0.getCount();
          //Serial.println(encoderCounts);
          goal = (int)(encoderCounts + (float)packet[2] * 35);
          //Serial.println(goal);
          while(abs(encoderCounts) < goal)
          {
            encoderCounts = motor0.getCount();
            //Serial.println(encoderCounts);
          }
          digitalWrite(motor1a, LOW);
          digitalWrite(motor1b, LOW);
          digitalWrite(motor2a, LOW);
          digitalWrite(motor2b, LOW);
        
*/ 
    
    
  


