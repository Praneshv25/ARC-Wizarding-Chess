//
// Created by Arnav Wadhwa on 9/13/23.
//

#ifndef Constants_h
#define Constants_h

#include <Arduino.h>

//
// IO Pin Definitions
//

const int LED_PIN = 0;

const int MOTOR_0_ENCODER_A = 0;
const int MOTOR_0_ENCODER_B = 1;
const int MOTOR_0_PWM_PIN = 2;

const int MOTOR_1_ENCODER_A = 2;
const int MOTOR_1_ENCODER_B = 3;
const int MOTOR_1_PWM_PIN = 4;

const int UART_TX_PIN = 4;
const int UART_RX_PIN = 5;


//
// Other Constants
//
const int DEFAULT_PWM_FREQUENCY = 1000;


#endif //Constants_h
