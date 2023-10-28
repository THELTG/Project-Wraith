Updated 25/10/2023

## Things achieved so far

- Powershell code execution via cmd (by using the powershell -enc method)
- AMSI bypass using Memory Patching (working on Windows 11)
- Windows Defender bypass using Invoke-ReflectivePEInjection (working on Windows 11)

## To Do List

- Find 2-3 more backup methods for AMSI bypass.
- Figure out how to bypass windows defender / disable windef without relying on the existing AMSI bypass, if possible.
- Figure out methods of PE and how to automate PE
- Make our bypass methods more stealthy, if possible.

## Things to read

Documentation for creating caldera plugins
https://caldera.readthedocs.io/en/latest/How-to-Build-Plugins.html

Batch script AV bypass (see if this works)
https://devdotpy.medium.com/how-i-evaded-windows-defender-with-a-batch-script-kinda-fd21acae35d2

## Things to clarify

Is the simulated environment that of a home network, or a corporate one?

