//#include <sys/_stdint.h>
//
// Created by Arnav Wadhwa on 9/12/23.
//

#include <Arduino.h>
// #include "TCPClient.h"

//
// Protocol for communication between the Pico-ESP8266 pair and the main server
//
// Commands are sent from the server to the client via TCP/IP. The client is the Pico/ESP8266 pair.
// The ESP8266 is acting like a WiFi antenna for the Pico. The Pico is the actual client that does all the work.
//
// Each client has a unique socket that the server uses to talk to the client. The server will determine which
// client it is talking to by a unique ID that is sent with the socket when the client connects to the server.


// Pico/ESP8266 communication constants
const int UART_BAUD_RATE = 115200;


// TCP/IP communication constants
const int TCP_Retry_Attempts = 3;
const uint8_t COMMAND_PACKET_HEADER = 0xaa;
const uint8_t ACKNOWLEDGE_PACKET_HEADER_WITH_NO_DATA = 0x77;  // These are random numbers to the best of my knowledge
const uint8_t ACKNOWLEDGE_PACKET_HEADER_WITH_DATA = 0x78;  // These are random numbers to the best of my knowledge


// state values for: getCommandState
static int getCommandState = 0;
const int GET_COMMAND_STATE__WAITING_FOR_HEADER = 0;
const int GET_COMMAND_STATE__WAITING_FOR_ADDRESS = 1;
const int GET_COMMAND_STATE__WAITING_FOR_COMMAND = 2;
const int GET_COMMAND_STATE__WAITING_FOR_DATA_SIZE = 3;
const int GET_COMMAND_STATE__WAITING_FOR_DATA = 4;
const int GET_COMMAND_STATE__WAITING_FOR_CHECKSUM = 5;


//
// vars global to this module
//
static int clientAddress = 0;
static int TXEnablePin;
static int TXEnableDelayUS = (1000000 * 2) / UART_BAUD_RATE;   // delay 2 serial bits
static uint8_t dataReceiveBuffer[16];
static int dataReceiveIndex;
static uint8_t dataTransmitBuffer[16];
static int dataTransmitIndex;


//
// external functions
//
extern void debug(const char *s);
extern void debug(const char *s, int i);


// ---------------------------------------------------------------------------------
//                                 Public functions
// ---------------------------------------------------------------------------------


//
// initialize the UART serial communication
//    Enter:  clientAddr = the address of this client (0 - 0x3f)
//            TXPin = pin number used to transmit the UART signal
//            RXPin = pin number used to receive the UART signal
//            txEnablePin = pin number used to enable client's UART TX signal
//
void UARTInitialize(int clientAddr, int TXPin, int RXPin, int txEnablePin)
{
    clientAddress = clientAddr;
    TXEnablePin = txEnablePin;
    // Serial1.setRX(RXPin);
    // Serial1.setTX(TXPin);
    Serial1.begin(UART_BAUD_RATE);
    getCommandState = GET_COMMAND_STATE__WAITING_FOR_HEADER;
}


