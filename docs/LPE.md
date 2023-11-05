## Notes

Two possible ways we can do LPE for Win 11 :

1. We discover a whole new vulnerability (not feasible)
2. Assume that all the target machines use Win 11, but they might be using different versions of it that are missing some patches.

Given that the tool is supposed to test out several post-exploitation payloads and generate a report that is supposed to say **exploit failed** or **exploit passed**, method 2 might be ok. to be confirmed with DSO

## Test 1 - CVE-2023-21768  (Failed)

A CVE that allows an attacker to elevate any process' privileges to SYSTEM. Patch released by Microsoft.

### References

https://github.com/chompie1337/Windows_LPE_AFD_CVE-2023-21768
https://securityintelligence.com/x-force/patch-tuesday-exploit-wednesday-pwning-windows-ancillary-function-driver-winsock/


## Test 2 - CVE-2023-36802   (Failed)

A CVE that allows an attacker to elevate any process' privileges to SYSTEM. Patch released by Microsoft.

### References

https://github.com/chompie1337/Windows_MSKSSRV_LPE_CVE-2023-36802
https://securityintelligence.com/x-force/critically-close-to-zero-day-exploiting-microsoft-kernel-streaming-service/