#include <winsock2.h>
#include <schannel.h>
#include <security.h>
#include <stdio.h>

#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "secur32.lib")

// Function to handle Schannel errors
void DisplaySChannelError(const char* message, SECURITY_STATUS status)
{
    fprintf(stderr, "%s: 0x%08x\n", message, status);
}

void SendEncryptedData(SOCKET clientSocket, SecHandle context, const char* data, size_t dataSize)
{
    SECURITY_STATUS status;
    SecBufferDesc outputBufferDesc;
    SecBuffer outputBuffer;

    outputBufferDesc.ulVersion = SECBUFFER_VERSION;
    outputBufferDesc.cBuffers = 1;
    outputBufferDesc.pBuffers = &outputBuffer;

    outputBuffer.BufferType = SECBUFFER_TOKEN;
    outputBuffer.cbBuffer = dataSize;
    outputBuffer.pvBuffer = (void*)data;

    status = EncryptMessage(&context, 0, &outputBufferDesc, 0);
    if (status != SEC_E_OK) {
        DisplaySChannelError("EncryptMessage failed", status);
        return;
    }

    // Now, send the encrypted data over the socket
    send(clientSocket, (const char*)outputBuffer.pvBuffer, outputBuffer.cbBuffer, 0);
}

void ReceiveEncryptedData(SOCKET clientSocket, SecHandle context)
{
    // Receive encrypted data from the server
    char buffer[1024];  // Adjust the buffer size based on your needs
    int bytesRead = recv(clientSocket, buffer, sizeof(buffer), 0);

    if (bytesRead > 0) {
        // Decrypt the received data
        SecBufferDesc inputBufferDesc;
        SecBuffer inputBuffer;

        inputBufferDesc.ulVersion = SECBUFFER_VERSION;
        inputBufferDesc.cBuffers = 1;
        inputBufferDesc.pBuffers = &inputBuffer;

        inputBuffer.BufferType = SECBUFFER_TOKEN;
        inputBuffer.cbBuffer = bytesRead;
        inputBuffer.pvBuffer = buffer;

        SECURITY_STATUS status = DecryptMessage(&context, &inputBufferDesc, 0, NULL);
        if (status != SEC_E_OK) {
            DisplaySChannelError("DecryptMessage failed", status);
            return;
        }

        // The decrypted data is now available in inputBuffer.pvBuffer
        printf("Received decrypted data: %.*s\n", inputBuffer.cbBuffer, (char*)inputBuffer.pvBuffer);
    }
}

// gcc attempt.c -o attempt.exe -lws2_32 -lsecur32
int main()
{
    fprintf(stdout,"[+] starting main.\n");
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        fprintf(stderr, "Failed to initialize Winsock\n");
        return 1;
    }
    fprintf(stdout,"[+] initialized winsock.\n");
    SOCKET clientSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (clientSocket == INVALID_SOCKET) {
        fprintf(stderr, "Failed to create socket\n");
        WSACleanup();
        return 1;
    }
    fprintf(stdout,"[+] successfully created socket\n");

    // Set up the server address structure
    struct sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = inet_addr("127.0.0.1");  // Replace with the server's IP
    serverAddr.sin_port = htons(9999);  // Replace with the server's port

    // Connect to the server
    if (connect(clientSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        fprintf(stderr, "Failed to connect to the server\n");
        closesocket(clientSocket);
        WSACleanup();
        return 1;
    }
    fprintf(stdout,"[+] successfully connected to the server\n");

    // Initialize Schannel
    SCHANNEL_CRED schannelCred;
    memset(&schannelCred, 0, sizeof(schannelCred));
    schannelCred.dwVersion = SCHANNEL_CRED_VERSION;

    // Set up other Schannel settings as needed

    CredHandle credHandle;
    SecHandle context;
    SECURITY_STATUS status;

    status = AcquireCredentialsHandle(NULL, UNISP_NAME, SECPKG_CRED_OUTBOUND, NULL, &schannelCred, NULL, NULL, &credHandle, NULL);
    if (status != SEC_E_OK) {
        DisplaySChannelError("AcquireCredentialsHandle failed", status);
        closesocket(clientSocket);
        WSACleanup();
        return 1;
    }
    fprintf(stdout,"[+] acquire credential handle success\n");

    // Set up the TLS context
    status = InitializeSecurityContext(&credHandle, NULL, "localhost", ISC_REQ_SEQUENCE_DETECT | ISC_REQ_REPLAY_DETECT | ISC_REQ_CONFIDENTIALITY | ISC_RET_EXTENDED_ERROR | ISC_REQ_ALLOCATE_MEMORY | ISC_REQ_STREAM, 0, SECURITY_NATIVE_DREP, NULL, 0, &context, NULL, NULL, NULL);
    if (status != SEC_I_CONTINUE_NEEDED) {
        DisplaySChannelError("InitializeSecurityContext failed", status);
        closesocket(clientSocket);
        WSACleanup();
        return 1;
    }
    fprintf(stdout,"[+] initialize security context success\n");

    // Continue with secure channel operations as needed

    // Send encrypted data to the server
    const char* sendData = "This is a test message.";
    SendEncryptedData(clientSocket, context, sendData, strlen(sendData));
    fprintf(stdout,"[+] sending out a test message\n");
    // Receive encrypted data from the server
    ReceiveEncryptedData(clientSocket, context);
    fprintf(stdout,"[+] receiving a message\n");
    // Clean up resources
    FreeCredentialsHandle(&credHandle);
    closesocket(clientSocket);
    WSACleanup();

    return 0;
}