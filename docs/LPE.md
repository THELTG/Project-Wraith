## Notes

Three possible ways we can do LPE for Win 11 :

1. We discover a whole new vulnerability (not feasible)
2. Assume that all the target machines use Win 11, but they might be using different versions of it that are missing some patches.
3. The Windows 11 installation has vulnerable drivers installed, which can be used as a vector for LPE

Given that the tool is supposed to test out several post-exploitation payloads and generate a report that is supposed to say **exploit failed** or **exploit passed**, method 2 might be ok. to be confirmed with DSO

## Test 1 - CVE-2023-21768  (Passed)

A CVE that allows an attacker to elevate any process' privileges to SYSTEM. Patch released by Microsoft.

	### References

https://github.com/chompie1337/Windows_LPE_AFD_CVE-2023-21768
https://securityintelligence.com/x-force/patch-tuesday-exploit-wednesday-pwning-windows-ancillary-function-driver-winsock/

Passed with Windows 11 22h2 OS build 22621.525
![](misc/Pasted%20image%2020231125214501.png)
## Test 2 - CVE-2023-36802   (Passed)

A CVE that allows an attacker to elevate any process' privileges to SYSTEM. Patch released by Microsoft.

	### References

https://github.com/chompie1337/Windows_MSKSSRV_LPE_CVE-2023-36802
https://securityintelligence.com/x-force/critically-close-to-zero-day-exploiting-microsoft-kernel-streaming-service/

![](misc/Pasted%20image%2020231125222408.png)

## Test 3 - Kernel Drivers (NVIDIA)

[https://security.gentoo.org/glsa/202310-02](https://security.gentoo.org/glsa/202310-02 "https://security.gentoo.org/glsa/202310-02")

https://nvidia.custhelp.com/app/answers/detail/a_id/5415

| CVE                | Driver Name |
| ------------------ | ----------- |
| **CVE-2022-34669** |             |
|                    |             |


As of now NVIDIA drivers are generally version 546.1*. 
![](misc/Pasted%20image%2020231125015314.png)