import socket
import threading

# Usage
# To initialize and use the server:
# >>> from PythonTestServer import ESPServer
# >>> server = ESPServer()
# To send a command:
# >>> server.send_command(1, bytearray([0x01, 0x02, ..., 0x10]))

#Byte array format:
    # Header
    # Command
    # Associated Data
    
#LOOK INTO INCREASE BYTE ARRAY SIZE, MIGHT NOT HAVE TO MAKE QUEUE FOR COMMANDS IF WE CAN JUST SEND
#A TON OF BYTES AT ONCE


class ESPServer:
    def __init__(self, port=12345):
        self.UDP_PORT = port
        self.BUFFER_SIZE = 128  # Set the buffer size to 16 bytes for the byte array Testing 64
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.UDP_PORT))

        self.devices = {}  # Mapping of device_id to IP_address

        # Start listening for messages on a new thread
        self.listen_thread = threading.Thread(target=self.start_listening)
        self.listen_thread.daemon = True  # Daemon threads will exit when the main program exits
        self.listen_thread.start()

    def start_listening(self):
        while True:
            data, addr = self.sock.recvfrom(self.BUFFER_SIZE)
            if len(data) <= 128:
                # Handle the initialization sequence and normal commands
                if data[0] == 0xaa:  # Check if this is an init packet
                    device_id = data[1]
                    checksum = data[2]
                    # Perform a simple checksum validation
                    if checksum == (device_id & 0xFF):
                        self.devices[device_id] = addr[0]
                        print(f"Device {device_id} initialized with IP {addr[0]}")
                    else:
                        print(f"Checksum mismatch for device ID {device_id}")
                else:
                    print(f"Received data from {addr[0]}: {data}")
            else:
                print(data)
                print(f"Invalid packet size from {addr[0]}")

    def send_command(self, device_id, command):
        if device_id in self.devices:
            UDP_IP = self.devices[device_id]
            # Check if the command is a bytearray, and its length is 16 or less
            if isinstance(command, bytearray) and len(command) <= 128:
                # Pad the command with zeros if it's less than 16 bytes
                self.sock.sendto(command, (UDP_IP, self.UDP_PORT))
            else:
                print(f"Command must be a bytearray with a length of 16 or less.")
        else:
            print(f"No device found with ID {device_id}")

