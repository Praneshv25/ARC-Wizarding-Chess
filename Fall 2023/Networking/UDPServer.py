import socket
import threading


class ESPServer:
    def __init__(self, port=12345):
        self.UDP_PORT = port
        self.BUFFER_SIZE = 1024
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
            data_str = data.decode('utf-8')
            print(f"Recieved packet data {data}, addr {addr}, str {data_str}")

            # If the message starts with "INIT:", it's an initialization message from an ESP8266
            if data_str.startswith("INIT:"):
                device_id = data_str.split(":")[1]
                self.devices[device_id] = addr[0]
                print(f"Device {device_id} connected with IP {addr[0]}")
            else:
                # Handle other messages here
                print(f"Received from {addr[0]}: {data_str}")

    def send_command(self, device_id, command):
        if device_id in self.devices:
            UDP_IP = self.devices[device_id]
            self.sock.sendto(command.encode('utf-8'), (UDP_IP, self.UDP_PORT))
        else:
            print(f"No device found with ID {device_id}")