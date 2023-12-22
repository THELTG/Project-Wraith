import pwn
import socket
import ssl
import threading

connections = []
connections_lock = threading.Lock()

def say_hello(ssl_socket:pwn.remote,addr):
    print(addr)
    print(ssl_socket.recv(1024,2))
    ssl_socket.sendline(b"Hello.")
    ssl_socket.close()

class SSL_Service:    
    def __init__(self,host,port,handler):
        self.host = host 
        self.port = port 
        self.handler = handler 
        # change if needed
        self.certificate = './credentials/certificate.pem'
        self.private_key = './credentials/private.pem'
        
    def run(self):
        global connections
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host,self.port))
        server_socket.listen(5)
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(self.certificate,self.private_key,None)
        while True:
            client_socket, addr = server_socket.accept()
            ssl_socket = context.wrap_socket(client_socket, server_side=True)
            ssl_socket = pwn.remote.fromsocket(ssl_socket)
            connections.append(ssl_socket) 
            threading.Thread(target=self.handler,args=(ssl_socket,addr)).start()

ssld = SSL_Service('0.0.0.0',9999,say_hello)
ssld.run()
print('hello')