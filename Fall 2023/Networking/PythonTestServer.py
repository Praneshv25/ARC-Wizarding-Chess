import atexit
import socket
import threading

# This script is a test and meant to be run from the python console.
# >>> from PythonTestServer import ESPServer
# >>> server = ESPServer()
# >>> server.send_command('ESP1', '1')


class ESPServer:
    def __init__(self, host='0.0.0.0', port=1234):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clients = {}

        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.start()

        # Register the cleanup function to be called on exit
        atexit.register(self.cleanup)

    def start_server(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection from {client_address}")

            client_id = client_socket.recv(1024).decode('utf-8')
            self.clients[client_id] = client_socket

    def send_command(self, client_id, command):
        if client_id in self.clients:
            try:
                self.clients[client_id].sendall(command.encode('utf-8'))
                response = self.clients[client_id].recv(1024)
                print(f"Response from {client_id}: {response.decode('utf-8')}")
            except Exception as e:
                print(f"Failed to communicate with {client_id}, with exception {e}")
        else:
            print(f"No client with ID: {client_id}")

    def cleanup(self):
        print("Cleaning up before exit...")

        # Close client connections
        for client_socket in self.clients.values():
            client_socket.close()

        # Close server socket
        self.server_socket.close()
        exit(0)
