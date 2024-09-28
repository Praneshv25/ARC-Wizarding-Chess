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
const int motor1b = 16;
const int l293Enable = 19;
const int motor2a = 13;
const int motor2b = 14;
const int l2932Enable = 15;
const int encoderA = 10;
const int encoder2A = 20;
int currentCommand[4] = {0};

PioEncoder motor0(encoderA);
PioEncoder motor1(encoder2A);
long encoderCounts = -999;
long goal = 0;
long newEncoderCounts;
int speed = 200;
int len = 0;



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
      //Serial.print("\n");


      if(dataIndex == len || (int)incomingPacket[dataIndex] == 0) //if data index at max value or no more commands in array
      {
        dataIndex = 3; //reset data index to start
        memset(incomingPacket,0,sizeof(incomingPacket)); //set data in the old data packet to 0
      } 


      char response = process_command(currentCommand);
      Serial1.write(response);
    }
}

char process_command(int packet[4]) {
    switch(packet[0]){
      case 1: //packet[1] == 0 = forward, packet[1] == 1 = backward
          move(packet[1],packet[2],packet[3]);
        return 'M';
      case 2: //90degree turn is roughly 3100 encoder counts
          motor0.reset();
          motor1.reset();
          //packet[1] == 0 = CCW, packet[1] == 1 = CW
          analogWrite(motor1a, (packet[1]*speed));
          analogWrite(motor1b, ((1-packet[1])*speed));
          analogWrite(motor2a, ((1-packet[1])*speed));
          analogWrite(motor2b, (packet[1]*speed));
          encoderCounts = motor0.getCount();
          //Serial.println(encoderCounts);
          goal = (int)(encoderCounts + (float)packet[2] * 34.4444);
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
        
        return 'T';
      case 3:
        digitalWrite(motor1a, LOW);
        digitalWrite(motor1b, LOW);
        digitalWrite(motor2a, LOW);
        digitalWrite(motor2b, LOW);
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
  analogWrite(motor1a, ((1-dir)*speed));
  analogWrite(motor1b, (dir*speed));
  analogWrite(motor2a, ((1-dir)*speed));
  analogWrite(motor2b, (dir*speed));
  encoderCounts = motor0.getCount();
  goal = encoderCounts + (counts1 * 256 + counts2) * 100;
  while(abs(encoderCounts) < goal)
  {
    encoderCounts = motor0.getCount();
  }
}
    
    
    
  


