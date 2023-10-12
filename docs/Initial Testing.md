
Done by: Koh Kai En 

The current setup environment contains the following items:

1) A fresh VMware installation of Windows 10
2) A bind tcp connection from the Win10 vm to emulate post exploitation
3) A python socket script to connect to the bind tcp

The Win10 VM has the following items installed/downloaded:

1) Wireshark-win64-4.0.10 installed
2) Ncat.exe standalone downloaded

The following users were made:

| Username | Password | User Account Type |
| ----------- | ------ | ---- |
| alice | china1 | Local User |
| bob | spiderman3 | Local User |
| johnathan | bubblegum | Administrator|

![](misc/Pasted%20image%2020231012195023.png)

This is the configurations used for the Win10 VM

![](misc/Pasted%20image%2020231012170011.png)

To test what the AMSI would look like when triggered, I will paste the following powershell reverse shell one-liner into the vm terminal.

We can see that the Antivirus software stopped the code from executing.
![](misc/Pasted%20image%2020231012172442.png)

The next step is to figure out how we can setup the bind shell for our python testing later on. 

In the Win10 VM, run the following command to allow your client machine to use cmd remotely.

```Command-Prompt
ncat -e cmd.exe -l 9999
```

![](misc/Pasted%20image%2020231012184532.png)

From the host machine connect to the VM via ncat on port 9999 and cmd.exe should appear.

![](misc/Pasted%20image%2020231012184548.png)

However, we are unable to open powershell due to AMSI blocking access 
![](misc/Pasted%20image%2020231012184723.png)

It will instead run powershell on the terminal that contains the netcat command and stop the connection.
![](misc/Pasted%20image%2020231012184734.png)

---
# Connecting via Python on Host


We can initiate a connection from python using the pwntools library.

```python
#python3.11 env 
from pwn import *
# change the IP_ADDRESS to your environment
IP_ADDRESS = '192.168.50.72'
PORT = 9999
# initiate connection

c = connect(IP_ADDRESS,PORT)
c.interactive()
c.close()
```

The script above imitates the ncat connection as conducted in the previous section, from here we can try to automate certain operations such as privilege escalation.

![](misc/Pasted%20image%2020231012191147.png)

The massive issue here is that AMSI is still blocking Powershell from being connected as stated above.

The below are some of the reasons why we need to use powershell and not cmd to automate the processes of privilege escalation / AV bypass.

1) Powershell is able to call and reference all the Windows APIs easily, while command prompt cannot.

For example, the ```Get-Acl``` command can be called in powershell

![](misc/Pasted%20image%2020231012193114.png)

But cannot be called in Command prompt

![](misc/Pasted%20image%2020231012193200.png)

