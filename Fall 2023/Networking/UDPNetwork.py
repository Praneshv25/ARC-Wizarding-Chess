# This code will live on the Raspberry Pi and will be used to communicate with all the clients

# Protocol for UDP serial communication between the Server and a Client module:
# 
# Commands are sent from the Server to a Client.
# The Client's address identifies the Client on the UDP network.
# Each Client must have a unique 6-bit ClientAddress.
#
# Commands from the Server include a CommandByte and up to 15 bytes of additional
# data.  The Client must acknowledge that it received the Server's command and that
# the data it received is intact.  The Server can send commands to have the Client
# do things, or it can send commands requesting data from the Client.
#
# When the Client receives a command from the Server, it must acknowledge the command.
# This acknowledgement is used to let the Server know the command was received
# successfully.  When the Server sends a command requesting data from the Client, the
# Client sends the data by adding it to the acknowledgement (which can include up
# to 15 bytes of data from the Client).
#
# After the Server sends a command, it waits for an acknowledgement from the Client.
# If the Server doesn't receive the acknowledgement within a few milliseconds, it
# resends the command (up to n times).  If the Client receives a command with corrupted
# data, the Client simply ignores the command by not executing it or sending any
# acknowledgement (causing the Server to resend).
# 
# The Server initiates all data transfers.  The Client cannot asynchronously
# transmit data not requested by a command from the Server.
#
# Byte format of command packets sent from the Server directly to the Client:
#   * HeaderByte: Always 0xaa
#   * CommandByte
#   * DataCount: Count of bytes in the DataField (0 - 15):
#      - The value's low nibble = DataCount
#      - The value's high nibble = (~DataCount) << 4   (one's compliment of the DataCount)
#   * DataField: Between 0 and 15 bytes of additional data sent by the Server
#   * Checksum: The 8 bit sum of all bytes in the packet including the HeaderByte, 
#              DataCount value, ClientAddress value, CommandByte, and all bytes in
#              the DataField.
#
# There are two packet formats the Client uses when acknowledging the Server's commands.
# If the Server isn't requesting data from the Client, the acknowledgement format is:
#   * HeaderByte: 0x77
#   * Checksum: (will always be 0x77)
# If the Server is requesting data from the Client, the format is:
#   * HeaderByte: 0x78
#   * DataCount: Count of bytes in the DataField (1 - 15):
#      - The value's low nibble = DataCount
#      - The value's high nibble = (~DataCount) << 4   (one's compliment of the DataCount)
#  * DataField: Between 1 and 15 bytes of data sent from the Client
#  * Checksum: The 8 bit sum of all bytes in the acknowledgement packet including the 
#              HeaderByte, DataCount value, and all bytes in the DataField.
# In addition to this, we need to send out a heartbeat every x seconds/minutes
# 	* HeaderByte: 0x79
# 	* Serial Number (of pico)
# 	* Checksum (will be 0x79 + serial number)
#
from time import time

#
# Server/Client communication constants
#
_UDP_RETRY_ATTEMPTS = 3
_COMMAND_PACKET_HEADER = 0xaa
_ACKNOWLEDGEMENT_PACKET_HEADER_WITH_NO_DATA = 0x77
_ACKNOWLEDGEMENT_PACKET_HEADER_WITH_DATA = 0x78

#
# state values for: receivePacketState
#
_RECEIVE_PACKET_STATE__WAITING_FOR_HEADER = 0
_RECEIVE_PACKET_STATE__WAITING_FOR_DATA_COUNT = 1
_RECEIVE_PACKET_STATE__WAITING_DATA = 2
_RECEIVE_PACKET_STATE__WAITING_FOR_CHECKSUM = 8

#
# vars global to this module
#
_dataTransmitBuffer = bytearray(16)
_dataTransmitIndex = 0
_dataReceiveBuffer = bytearray(16)
_dataReceiveIndex = 0


class UDPNetwork:
    #
    # initialize the UDP serial communication
    #
    def __init__(self):
        global _dataTransmitIndex
        global _dataReceiveIndex

        _dataTransmitIndex = 0
        _dataReceiveIndex = 0

    #
    # send a command to a Client module via a UDP network, command's additional data must have
    # already been "Pushed". After this function returns data from the Client is retrieved by "Popping"
    #    Enter:  ClientAddress = address of Client module (0 - 0x3f)
    #            command = command byte
    #            timeoutPeriodMS = number of milliseconds to wait for the Client to respond
    #    Exit:   [0]: True returned on success, else False
    #            [1]: number of failed packets (0 = no failed packets)
    #
    def sendCommand(self, ClientAddress: int, command: int, timeoutPeriodMS: int):
        global serialPort, retryCount, bytesReceivedCount
        global _dataTransmitIndex
        global _dataTransmitBuffer
        global _dataReceiveIndex
        global _dataReceiveBuffer
        receivePacketState = _RECEIVE_PACKET_STATE__WAITING_FOR_HEADER
        timeoutPeriodSec = timeoutPeriodMS / 1000.0

        #
        # set up a loop to send a packet to Client, retrying if it fails
        #
        sendDataSize = _dataTransmitIndex
        _dataTransmitIndex = 0
        sendDataCountValue = (sendDataSize & 0x0f) + (((~sendDataSize) & 0x0f) << 4)
        ClientAddressValue = (ClientAddress & 0x3f) | 0x80

        for retryCount in range(0, _UDP_RETRY_ATTEMPTS):
            #
            # send a packet to Client
            #
            packet = bytearray(5 + sendDataSize)
            checksum = 0

            packet[0] = _COMMAND_PACKET_HEADER
            checksum += _COMMAND_PACKET_HEADER

            packet[1] = ClientAddressValue
            checksum += ClientAddressValue

            packet[2] = command
            checksum += command

            packet[3] = sendDataCountValue
            checksum += sendDataCountValue

            for i in range(0, sendDataSize):
                packet[4 + i] = _dataTransmitBuffer[i]
                checksum += _dataTransmitBuffer[i]

            packet[4 + sendDataSize] = checksum % 0x100

            #
            # get acknowledgement packet from Client, timing out if it isn't received (or received corrupted)
            #
            startTime = time()
            receivePacketState = _RECEIVE_PACKET_STATE__WAITING_FOR_HEADER
            receivedDataSize = 0
            checksum = 0

            while True:
                #
                # check if timed out while waiting for Client's response
                #
                elapsedTime = time() - startTime
                if elapsedTime > timeoutPeriodSec:
                    break  # timed out, exit "while loop" causing packet to be resent to Client

                #
                # check if there's a new byte of data from the Client
                #
                if serialPort.inWaiting() == 0:
                    continue

                c = serialPort.read()[0]
                if receivePacketState == _RECEIVE_PACKET_STATE__WAITING_FOR_HEADER:
                    checksum += c
                    if c == _ACKNOWLEDGEMENT_PACKET_HEADER_WITH_NO_DATA:
                        receivePacketState = _RECEIVE_PACKET_STATE__WAITING_FOR_CHECKSUM

                    if c == _ACKNOWLEDGEMENT_PACKET_HEADER_WITH_DATA:
                        receivePacketState = _RECEIVE_PACKET_STATE__WAITING_FOR_DATA_COUNT

                elif receivePacketState == _RECEIVE_PACKET_STATE__WAITING_FOR_DATA_COUNT:
                    checksum += c
                    receivedDataSize = c & 0x0f
                    bytesReceivedCount = 0
                    _dataReceiveIndex = 0

                    if receivedDataSize == 0:
                        receivePacketState = _RECEIVE_PACKET_STATE__WAITING_FOR_HEADER
                    elif receivedDataSize != (((~c) >> 4) & 0x0f):
                        receivePacketState = _RECEIVE_PACKET_STATE__WAITING_FOR_HEADER
                    else:
                        receivePacketState = _RECEIVE_PACKET_STATE__WAITING_DATA

                elif receivePacketState == _RECEIVE_PACKET_STATE__WAITING_DATA:
                    checksum += c
                    _dataReceiveBuffer[bytesReceivedCount] = c
                    bytesReceivedCount += 1

                    if bytesReceivedCount == receivedDataSize:
                        receivePacketState = _RECEIVE_PACKET_STATE__WAITING_FOR_CHECKSUM;

                elif receivePacketState == _RECEIVE_PACKET_STATE__WAITING_FOR_CHECKSUM:
                    if c == checksum % 0x100:
                        return True, retryCount

                    receivePacketState = _RECEIVE_PACKET_STATE__WAITING_FOR_HEADER

                else:
                    receivePacketState = _RECEIVE_PACKET_STATE__WAITING_FOR_HEADER

        return False, retryCount + 1

    #
    # push data to the transmit buffer
    #
    def pushUint8(self, value: int):
        global _dataTransmitIndex
        global _dataTransmitBuffer
        _dataTransmitBuffer[_dataTransmitIndex] = value & 0xff
        _dataTransmitIndex += 1

    def pushInt8(self, value: int):
        global _dataTransmitIndex
        global _dataTransmitBuffer
        _dataTransmitBuffer[_dataTransmitIndex] = value & 0xff
        _dataTransmitIndex += 1

    def pushUint16(self, value: int):
        global _dataTransmitIndex
        global _dataTransmitBuffer
        _dataTransmitBuffer[_dataTransmitIndex] = (value >> 8) & 0xff
        _dataTransmitIndex += 1
        _dataTransmitBuffer[_dataTransmitIndex] = value & 0xff
        _dataTransmitIndex += 1

    def pushInt16(self, value: int):
        global _dataTransmitIndex
        global _dataTransmitBuffer
        _dataTransmitBuffer[_dataTransmitIndex] = (value >> 8) & 0xff
        _dataTransmitIndex += 1
        _dataTransmitBuffer[_dataTransmitIndex] = value & 0xff
        _dataTransmitIndex += 1

    def pushUint32(self, value: int):
        global _dataTransmitIndex
        global _dataTransmitBuffer
        _dataTransmitBuffer[_dataTransmitIndex] = (value >> 24) & 0xff
        _dataTransmitIndex += 1
        _dataTransmitBuffer[_dataTransmitIndex] = (value >> 16) & 0xff
        _dataTransmitIndex += 1
        _dataTransmitBuffer[_dataTransmitIndex] = (value >> 8) & 0xff
        _dataTransmitIndex += 1
        _dataTransmitBuffer[_dataTransmitIndex] = value & 0xff
        _dataTransmitIndex += 1

    def pushInt32(self, value: int):
        global _dataTransmitIndex
        global _dataTransmitBuffer
        _dataTransmitBuffer[_dataTransmitIndex] = (value >> 24) & 0xff
        _dataTransmitIndex += 1
        _dataTransmitBuffer[_dataTransmitIndex] = (value >> 16) & 0xff
        _dataTransmitIndex += 1
        _dataTransmitBuffer[_dataTransmitIndex] = (value >> 8) & 0xff
        _dataTransmitIndex += 1
        _dataTransmitBuffer[_dataTransmitIndex] = value & 0xff
        _dataTransmitIndex += 1

    #
    # get data from the receive buffer
    #
    def popUint8(self) -> int:
        global _dataReceiveIndex
        global _dataReceiveBuffer
        value = _dataReceiveBuffer[_dataReceiveIndex]
        _dataReceiveIndex += 1
        return value

    def popInt8(self) -> int:
        global _dataReceiveIndex
        global _dataReceiveBuffer
        value = _dataReceiveBuffer[_dataReceiveIndex]
        if value & 0x80 > 0:
            value -= 0x100
        _dataReceiveIndex += 1
        return value

    def popUint16(self) -> int:
        global _dataReceiveIndex
        global _dataReceiveBuffer
        value = ((_dataReceiveBuffer[_dataReceiveIndex] << 8) + _dataReceiveBuffer[_dataReceiveIndex + 1])
        _dataReceiveIndex += 2
        return value

    def popInt16(self) -> int:
        global _dataReceiveIndex
        global _dataReceiveBuffer
        value = ((_dataReceiveBuffer[_dataReceiveIndex] << 8) + _dataReceiveBuffer[_dataReceiveIndex + 1])
        if value & 0x8000 > 0:
            value -= 0x10000
        _dataReceiveIndex += 2
        return value

    def popUint32(self) -> int:
        global _dataReceiveIndex
        global _dataReceiveBuffer
        value = ((_dataReceiveBuffer[_dataReceiveIndex] << 24) +
                 (_dataReceiveBuffer[_dataReceiveIndex + 1] << 16) +
                 (_dataReceiveBuffer[_dataReceiveIndex + 2] << 8) +
                 (_dataReceiveBuffer[_dataReceiveIndex + 3]))
        _dataReceiveIndex += 4
        return value

    def popInt32(self) -> int:
        global _dataReceiveIndex
        global _dataReceiveBuffer
        value = ((_dataReceiveBuffer[_dataReceiveIndex] << 24) +
                 (_dataReceiveBuffer[_dataReceiveIndex + 1] << 16) +
                 (_dataReceiveBuffer[_dataReceiveIndex + 2] << 8) +
                 (_dataReceiveBuffer[_dataReceiveIndex + 3]))
        if value & 0x80000000 > 0:
            value -= 0x100000000
        _dataReceiveIndex += 4
        return value
