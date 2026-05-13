# Sockets

In this part of the documentation, we will cover:
- [What is a socket?](#what-is-a-socket)
- [How TCP communication works](#how-tcp-communication-works)
- [How Python sockets behave](#how-python-sockets-behave)
- [Why port scanners rely on sockets](#why-port-scanners-rely-on-sockets)
- [How the scanner uses them internally](#how-the-scanner-uses-them-internally)

## What is a socket?
A socket is an endpoint for communication between two machines. It is a software structure that allows programs to send and receive data over a network. Sockets are used in various types of network communication, including TCP/IP, UDP, and more. Networking APIs expose sockets as a way for applications to interact with the underlying network protocols.
e.g. See this analogy phone call endpoint - the phone number is like the IP address, and the specific line you are using(the door/channel) to make the call is like the port number. The socket is the combination of the IP address and port number that allows you to connect to a specific service on a remote machine.

## Client-Server Communication
In a typical client-server communication model, the server listens for incoming connections on a specific port. When a client wants to connect to the server, it creates a socket and attempts to establish a connection to the server's IP address and port. If the connection is successful, the client and server can exchange data through the socket.
`Client (socket) --> Server:80 (socket)`

### Web servers
For example, a web server typically listens on port 80 for HTTP requests. When a client (like a web browser) wants to access a website, it creates a socket and connects to the server's IP address on port 80. If the connection is successful, the client can send an HTTP request to the server, and the server can respond with the requested web page.

```Python
import socket
# Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the server
s.connect(('example.com', 80))
# Send an HTTP request
s.sendall(b'GET / HTTP/1.1\r\nHost: example.com\r
\n\r\n')
# Receive the response
response = s.recv(4096)
print(response.decode())
# Close the socket
s.close()
```
### SSH servers
Similarly, an SSH server listens on port 22 for incoming SSH connections. When a client (like an SSH client) wants to connect to the server, it creates a socket and connects to the server's IP address on port 22. If the connection is successful, the client can authenticate and establish a secure shell session with the server.

```Python
import socket
# Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the SSH server
s.connect(('example.com', 22))
# Send an SSH request (this is just a placeholder, actual SSH communication is more complex)
s.sendall(b'SSH-2.0-MySSHClient\r\n')
# Receive the response
response = s.recv(4096)
print(response.decode())
# Close the socket
s.close()
```
### Telnet services
Telnet services typically listen on port 23. When a client (like a Telnet client) wants to connect to the server, it creates a socket and connects to the server's IP address on port 23. If the connection is successful, the client can interact with the server through a command-line interface. But keep in mind that Telnet is an unencrypted protocol and is generally considered insecure for modern use. Modern alternatives like SSH are preferred for secure remote access.

## What is a Port?
A port is a logical endpoint for communication on a network. It is a 16-bit number that ranges from 0 to 65535 and is used to identify specific services or applications running on a machine. When a client connects to a server, it specifies the port number to indicate which service it wants to access. For example, port 80 is commonly used for HTTP, port 22 for SSH, and port 23 for Telnet. Each service typically listens on a specific port, allowing clients to connect to the correct service based on the port number they specify.

IP defines the machine's address on the network, while the port number identifies the specific service or application running on that machine. Together, they form a socket that allows for communication between the client and server.

`e.g. 22 -> SSH  
      80 -> HTTP
      23 -> Telnet
      443 -> HTTPS`

Port scanning matters because it allows attackers to identify which services are running on a target machine. By scanning for open ports, attackers can determine which services are available and potentially vulnerable to exploitation. For example, if an attacker finds that port 22 (SSH) is open, they may attempt to brute-force the SSH credentials or look for known vulnerabilities in the SSH service. Similarly, if port 80 (HTTP) is open, they may look for vulnerabilities in the web server software or web applications running on that port. Therefore, understanding how sockets and ports work is crucial for both attackers and defenders in the context of network security.

## TCP vs UDP
TCP (Transmission Control Protocol) and UDP (User Datagram Protocol) are two different transport layer protocols that use sockets for communication. 

**TCP(connection-oriented)** is a connection-oriented protocol that provides reliable, ordered, and error checked delivery of data between applications. It establishes a connection between the client and server before data is transmitted, and it ensures that all data is received correctly and in the correct order. TCP is commonly used for applications that require reliability, such as web browsing, email, and file transfers.

**UDP(connectionless)**, on the other hand, UDP is a connectionless protocol that does not guarantee reliable delivery of data but it is fast in delivering data. It does not establish a connection before sending data and does not ensure that all data is received correctly or in the correct order. UDP is commonly used for applications that require low latency and can tolerate some loss of data, such as video streaming, online gaming, and VoIP (Voice over IP).

In summary, TCP is used for applications that require reliability and ordered delivery of data, while UDP is used for applications that require low latency and can tolerate some loss of data.

## TCP Three-Way Handshake
The TCP three-way handshake is a process used to establish a reliable connection between a client and a server. It involves three steps:
1. **SYN**: The client sends a SYN (synchronize) packet to the server to initiate the connection. This packet contains a random sequence number that the client will use to identify the connection.
2. **SYN-ACK**: The server responds with a SYN-ACK (synchronize-acknowledge) packet, which acknowledges the client's SYN and includes its own random sequence number.
3. **ACK**: The client sends an ACK (acknowledge) packet back to the server, acknowledging the server's SYN-ACK. At this point, the connection is established, and both the client and server can begin exchanging data.
` Client --> SYN
  Server --> SYN-ACK
  Client --> ACK`

```Python
# Example of TCP three-way handshake using Python sockets
import socket
# Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the server (this will initiate the three-way handshake)
s.connect(('example.com', 80))
# At this point, the three-way handshake is complete, and we can send data
s.sendall(b'GET / HTTP/1.1\r\nHost: example.com\r\n\r\n')
# Receive the response
response = s.recv(4096)
print(response.decode())
# Close the socket
s.close()
```
In this example, when the `connect` method is called, the TCP three-way handshake is automatically performed by the underlying socket implementation. The client sends a SYN packet, the server responds with a SYN-ACK, and the client sends an ACK to establish the connection before any data is sent. This process ensures that both the client and server are ready to communicate and that the connection is reliable before any data is exchanged. 


## Creating a Socket in Python
In Python, you can create a socket using the `socket` module. Here's a simple example of how to create a TCP socket and connect to a server:
```Python
import socket
# Create a TCP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the server (replace 'example.com' and 80 with the desired IP and port)
s.connect(('example.com', 80))
```
`AF_INET` specifies that we are using IPv4 addresses, if we wenat to use IPv6 we would use `AF_INET6`.
`IPv4` is the most widely used version of the Internet Protocol, which uses 32-bit addresses to identify devices on a network. It allows for approximately 4.3 billion unique addresses. `IPv6`, on the other hand, is the newer version of the Internet Protocol that uses 128-bit addresses, allowing for a vastly larger number of unique addresses (approximately 3.4 x 10^38). IPv6 was developed to address the limitations of IPv4, particularly the exhaustion of available IPv4 addresses.
`SOCK_STREAM` specifies that we want to create a TCP socket. If we wanted to create a UDP socket, we would use `SOCK_DGRAM` instead.
**TCP streams** provide a reliable, ordered, and error-checked delivery of data between applications. They establish a connection between the client and server before data is transmitted, ensuring that all data is received correctly and in the correct order. This makes TCP suitable for applications that require reliability, such as web browsing, email, and file transfers.
**UDP datagrams**, on the other hand, are connectionless and do not guarantee reliable delivery of data. They do not establish a connection before sending data and do not ensure that all data is received correctly or in the correct order. This makes UDP suitable for applications that require low latency and can tolerate some loss of data, such as video streaming, online gaming, and VoIP (Voice over IP).

## Blocking Sockets
By default, sockets in Python are blocking(waits for network events), which means that when you call a method like `recv()`, the program will wait (or block) until data is received before it continues executing. This can be problematic if you want to perform other tasks while waiting for data, as the program will be unresponsive during that time. To avoid this, you can set the socket timeout `settimeout(seconds)` method. This allows you to specify a timeout period for blocking socket operations. If the operation takes longer than the specified timeout, a `socket.timeout` exception will be raised, allowing your program to continue executing and handle the situation accordingly.
```Python
import socket
# Create a TCP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Set a timeout of 5 seconds for blocking operations
s.settimeout(5)
```
## `connect()` vs `connect_ex()`
The `connect()` method is used to establish a connection to a remote socket. If the connection is successful, it returns `None`. However, if the connection fails, it raises a `socket.error` exception. This can be problematic if you want to handle connection failures gracefully without using exception handling.

`connect_ex()` method, on the other hand, is a non-blocking version of `connect()`. It attempts to establish a connection to a remote socket, but instead of raising an exception on failure, it returns an error code. If the connection is successful, it returns `0`. If the connection fails, it returns a non-zero error code that indicates the reason for the failure. This allows you to handle connection failures more easily without needing to use exception handling.

## Sending Data `send()`
The `send()` method is used to send data through a socket. It takes a bytes-like object as an argument and sends it to the connected remote socket. The method returns the number of bytes sent, which may be less than the length of the data you intended to send. This can happen if the underlying network buffer is full or if there are other issues with the connection. Therefore, it's important to check the return value of `send()` to ensure that all data has been sent successfully.

## Receiving Data `recv()`
The `recv()` method is used to receive data from a socket. It takes a buffer size as an argument, which specifies the maximum amount of data to be received at once. The method returns a bytes object containing the data received from the remote socket. If the connection is closed by the remote socket, `recv()` will return an empty bytes object (`b''`). It's important to check the return value of `recv()` to determine if the connection has been closed or if data has been received successfully.

```Python
import socket
# Create a TCP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the server
s.connect(('example.com', 80))
# Send an HTTP request
request = b'GET / HTTP/1.1\r\nHost: example.com\r\n
\r\n'
bytes_sent = s.send(request)
print(f'Bytes sent: {bytes_sent}')
# Receive the response
response = s.recv(4096)
print(response.decode())
# Close the socket
s.close()
```
In this example, we create a TCP socket, connect to a server, and send an HTTP request. We then check the number of bytes sent using the return value of the `send()` method. If the number of bytes sent is less than the length of the request, it indicates that not all data was sent successfully, and you may need to handle this situation accordingly (e.g., by retrying the send operation or logging an error) and then we receive the response from the server using the `recv()` method. We check the return value of `recv()` to ensure that we have received data successfully and that the connection has not been closed by the remote socket. Finally, we close the socket to free up system resources.

## Encoding and Decoding Data
When sending and receiving data through sockets, it's important to remember that the data must be in bytes format. This means that if you want to send a string, you need to encode it into bytes before sending, and when you receive data, you may need to decode it back into a string for processing.
`Sockets send bytes --> Human reads strings --> Sockets receive bytes`

```Python
import socket
# Create a TCP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the server
s.connect(('example.com', 80))
# Send an HTTP request (encode the string to bytes)
request = 'GET / HTTP/1.1\r\nHost: example.com\r\n\r\n'
s.send(request.encode())
# Receive the response (decode the bytes to a string)
response = s.recv(4096)
print(response.decode())
# Close the socket
s.close()
```
## Why Some Services Send Bannes Automatically
Some services may automatically send banners when a connection is established. A banner is a message that a server sends to a client upon connection, often containing information about the service or software running on the server
. For example, when you connect to an SSH server, it may send a banner that includes the SSH version and the server's hostname. This can be useful for administrators to identify the service and its version, but it can also be exploited by attackers to gather information about the target system. Attackers can use this information to identify potential vulnerabilities in the service or software running on the server, which can be used to launch attacks. Therefore, it's important for administrators to be aware of the banners their services are sending and to consider whether they want to disable them or limit the information they provide to reduce the risk of information disclosure.

## Socket Errors and Network Failures
When working with sockets, it's important to be aware of potential errors and network failures that can occur. Some common socket errors include:
- `socket.timeout`: This error occurs when a socket operation exceeds the specified timeout period. It indicates that the operation took too long to complete, which can happen if the network is slow or if the remote server is unresponsive.
- `socket.error`: This is a general error that can occur for various reasons, such as a connection failure, a broken pipe, or an invalid socket operation.
- `resets`: This can happen when the remote server closes the connection unexpectedly, which can occur due to network issues, server crashes, or other problems on the remote side.
- `unreachable hosts`: This can occur when the target host is not reachable due to network issues, such as a firewall blocking the connection, a routing problem, or the target host being offline.
- `DNS failures`: This can happen when the domain name cannot be resolved to an IP address, which can occur due to issues with the DNS server, incorrect domain names, or network problems.

## Resource Cleanup
When working with sockets, it's important to ensure that you properly clean up resources to avoid issues such as memory leaks or exhausted file descriptors. This typically involves closing the socket when you're done using it. In Python, you can use the `close()` method to close a socket and free up system resources. The `with` keyword can also be used to automatically manage the lifecycle of a socket, ensuring that it is properly closed even if an error occurs. Here's an example of how to use `with` to manage a socket:

```Python
import socket
# Create a TCP socket and manage it with 'with' to ensure proper cleanup
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Connect to the server
    s.connect(('example.com', 80))
```
**`Finally, it's important to remember that sockets are a powerful tool for network communication, but they require careful handling to ensure that your applications are robust and secure. Always be mindful of potential errors, handle exceptions gracefully, and ensure that you clean up resources properly to maintain the stability and security of your applications.`**

