//
// Created by Tianyi on 11/2/23.
//

// TCPClient.cpp
#include "TCPClient.h"
#include <iostream>
#include <cstring>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

TCPClient::TCPClient(const std::string& serverAddress, int serverPort)
        : clientSocket(-1), serverAddress(serverAddress), serverPort(serverPort) {
}

TCPClient::~TCPClient() {
    // Disconnect();
    return;
}

bool TCPClient::Connect() {
    clientSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (clientSocket == -1) {
        std::cerr << "Socket creation failed." << std::endl;
        return false;
    }

    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(serverPort);
    serverAddr.sin_addr.s_addr = inet_addr(serverAddress.c_str());

    if (connect(clientSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) == -1) {
        std::cerr << "Connection failed." << std::endl;
        close(clientSocket);
        return false;
    }

    return true;
}

bool TCPClient::SendMessage(const std::string& message) {
    Connect();
    if (send(clientSocket, message.c_str(), message.size(), 0) == -1) {
        std::cerr << "Error sending data." << std::endl;
        return false;
    }
    return true;
}

bool TCPClient::ReceiveMessage(std::string& receivedMessage) {
    char buffer[1024];
    int bytesReceived = recv(clientSocket, buffer, sizeof(buffer), 0);
    if (bytesReceived <= 0) {
        std::cerr << "Connection closed by the server." << std::endl;
        return false;
    }
    buffer[bytesReceived] = '\0';
    receivedMessage = buffer;
    return true;
}

void TCPClient::Disconnect() {
    if (clientSocket != -1) {
        close(clientSocket);
        clientSocket = -1;
    }
}




//
//UDPTransceiver::UDPTransceiver(const std::string& serverIP, int serverPort)
//        : serverIP(serverIP), serverPort(serverPort) {
//    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
//    if (sockfd < 0) {
//        perror("Error opening socket");
//    }
//}
//
//
//UDPTransceiver::~UDPTransceiver() {
//    close(sockfd);
//}
//
//
//// Send a UDP message to the server
//void UDPTransceiver::Send(const std::string& message) {
//    struct sockaddr_in serverAddr;
//    serverAddr.sin_family = AF_INET;
//    serverAddr.sin_port = htons(serverPort);
//    serverAddr.sin_addr.s_addr = inet_addr(serverIP.c_str());
//
//    if (sendto(sockfd, message.c_str(), message.length(), 0, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
//        perror("Error sending data");
//    }
//}
//
//
//// Receive a UDP message from the server
//std::string UDPTransceiver::Receive() {
//    char buffer[BUFFER_SIZE];
//    struct sockaddr_in clientAddr;
//    socklen_t clientLen = sizeof(clientAddr);
//
//    ssize_t n = recvfrom(sockfd, buffer, BUFFER_SIZE, 0, (struct sockaddr*)&clientAddr, &clientLen);
//    if (n < 0) {
//        perror("Error receiving data");
//        return "";
//    }
//
//    buffer[n] = '\0';
//    return std::string(buffer);
//}