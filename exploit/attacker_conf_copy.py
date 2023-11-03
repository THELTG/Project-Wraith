payload_dir = './payloads'


# Set which of the two modes to listen (both port 9999)
listen_tcp = False
reverse_tcp = True

# setting what payload to use
meterpreter = True
caldera = False

# configuration for each payload
# still a work in progress

conf_meterpreter = {
    'file' : 'meterpreter.exe'
}
conf_caldera = {
    'webremote' : f'http'
}

# obfuscation level setter
bypasslevel = 3

# change the IP_ADDRESS to your environment
VICTIM_IP = '192.168.137.129'
VICTIM_PORT = 9999

HOST_IP = '192.168.137.1'
HOST_PORT = 5555

CALDERA_IP = '192.168.32.130'
CALDERA_WEB_PORT = 8888
CALDERA_SOCKET_PORT = 7010