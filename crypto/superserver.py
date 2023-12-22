from pwn import *
import socket
import ssl
import threading

class SSLServer:
    def __init__(self, host, port, handler, certfile, keyfile):
        self.host = host
        self.port = port
        self.handler = handler
        self.certfile = certfile
        self.keyfile = keyfile

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        while True:
            client_socket, addr = server_socket.accept()
            ssl_socket = context.wrap_socket(client_socket, server_side=True)
            threading.Thread(target=self.handler, args=(ssl_socket, addr)).start()

def handle_client(ssl_socket, addr):
    # Use pwnlib to interact with the SSL socket
    client = remote.fromsocket(ssl_socket)
    # Your code to handle the client goes here
    # For example, you can use client.recv() and client.send()
    print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
    
    data = client.recv(1024)
    print(f"Received data: {data.decode('utf-8')}")
    client.send(b"Hello from the server!\n")
    # Close the connection
    client.close()
    print(f"[*] Connection with {addr[0]}:{addr[1]} closed")

# Specify the server host and port
host = '0.0.0.0'
port = 12345

# Load your SSL certificate and private key (use absolute paths)
certfile = './credentials/certificate.pem'
keyfile = './credentials/private.pem'

# Create the SSLServer instance
server = SSLServer(host, port, handle_client, certfile, keyfile)

print(f"[*] Listening on {host}:{port} with SSL")

try:
    server.run()
except KeyboardInterrupt:
    print("[*] Server shutting down")