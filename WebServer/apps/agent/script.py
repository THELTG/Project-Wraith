import subprocess
import sys

#python .\script.py <IP> <PORT>
#e.g python .\script.py 127.0.0.1 8081

#IP to Int
def ip_to_int(ip_addr):
    ip_int = 0
    shift = 24
    octets = ip_addr.split(".")
    for octet in octets:
        octet = int(octet)
        ip_int |= (octet << shift)
        shift -= 8
    return ip_int

#Check Args
if len(sys.argv) != 3:
    print("Usage: python script.py <IP_ADDRESS> <PORT>")
    sys.exit(1)

#Parse Args
ip_addr = sys.argv[1]
port = int(sys.argv[2])

#Compile
compile= f"gcc agent.c -DIP_ADDRESS={ip_to_int(ip_addr)} -DPORT={port} -o agent -IE:/Mysys2/ucrt64/include/openssl -lssl -lcrypto -lws2_32 -static"
try:
    subprocess.run(compile, shell=True, check=True)
    print("Compile Success")
except:
    print("Compile Failed")
