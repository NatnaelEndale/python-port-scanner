# How the scanner identifies services and handles unpredictable network behavior 

We will discuss these topics in more detail in this section:
- [What is Banner Grabbing?](#what-is-banner-grabbing)
- [Passive and Active Service Detection](#passive-and-active-service-detection)
- [HTTP Probing](#http-probing)
- [Why some ports return No Banner?](#why-some-ports-return-no-banner)
- [Network errors and unpredictablity](#network-errors-and-unpredictablity)
- [Error handling strategy](#error-handling-strategy)
- [Exception types handled](#exception-types-handled)
- [Why `connect_ex()` helps error handling?](#why-connect_ex-helps-error-handling)
- [Real-world limitations of banner Grabbing](#real-world-limitations-of-banner-grabbing)
- [Security implications](#security-implications)
- [Problems encountered during development](#problems-encountered-during-development)
- [Future improvements](#future-improvements)

## Introduction
An open port only indicates that a service is listening, but it doesn't always reveal what that service is. To identify the service running on an open port, we can use a technique called banner grabbing. This involves sending specific requests to the service and analyzing the responses to determine its identity.

## What is Banner Grabbing?
Banner grabbing is a method used to gather information about a service running on an open port. It involves sending specific requests to the service and analyzing the responses to determine its identity.

Some services send a banner when a connection is established, which can include information about the service type and version. For example, an HTTP server might respond with a banner that includes the server software and version number.

Scanners can capture these banners to identify the service running on the open port. However, not all services provide banners, and some may provide misleading information.

Banners reveal information about the service/software running on the open port, which can be useful for identifying vulnerabilities and potential attack vectors. However, relying solely on banners can be risky, as they may not always be accurate or present.

## Passive and Active Service Detection

### Passive Service Detection
Passive service detection involves analyzing the traffic and responses from the service without actively sending requests. This can include looking for specific patterns in the responses or analyzing the behavior of the service to infer its identity. 
e.g. - SSH
     - Telnet

### Active Service Detection
Active service detection involves sending specific requests to the service and analyzing the responses to determine its identity. This can include sending HTTP requests to an open port and analyzing the responses to identify the service running on that port.
e.g. - HTTP

## HTTP Probing
HTTP probing is a common method used in active service detection to identify web servers. It involves sending HTTP requests to an open port and analyzing the responses to determine if a web server is running on that port. This can include looking for specific headers in the response, such as the Server header, which can provide information about the web server software and version.

```python
HEAD / HTTP/1.1\r\n
```
-**`HEAD`**: This is the HTTP method used to request the headers of a resource without fetching the actual content. It allows us to check if a web server is running and gather information about it without downloading the entire page. 
-**`Host`**: This header specifies the domain name of the server we are trying to access. It is required for HTTP/1.1 requests and helps the server determine which website or service we are trying to reach, especially if multiple sites are hosted on the same server.

Why HTTP requires applicayion-layer interaction? Because HTTP is an application-layer protocol, it requires a specific format for requests and responses. To identify if a service is running on an open port, we need to send a properly formatted HTTP request and analyze the response. This is why we use HTTP probing as part of our active service detection strategy.

## Why some ports return No Banner?
Some services may not provide a banner when a connection is established, which can make it difficult to identify the service running on the open port. This can be due to various reasons, such as security measures implemented by the service to prevent information disclosure, or simply because the service does not provide a banner by default. In such cases, we may need to use other techniques, such as analyzing the behavior of the service or sending specific requests to elicit a response that can help identify the service. 

## Network errors and unpredictablity
When scanning for services, we may encounter various network errors and unpredictable behavior. This can include timeouts, connection refusals, or unexpected responses from the service. These issues can arise due to network congestion, firewall rules, or misconfigured services. To handle these situations, we need to implement robust error handling strategies in our scanner to ensure that it can continue scanning other ports and services without crashing or getting stuck.

## Error handling strategy

The sacnner should not crash or get stuck when it encounters a failed port. Instead, it should log the error and continue scanning other ports and services. This way, we can ensure that the scanner can still provide valuable information about the services running on the target system, even if some ports are not responsive or do not provide banners.

## Exception types handled
When implementing error handling in our scanner, we should consider handling various types of exceptions that may occur during the scanning process. This can include:
- `socket.timeout`: This exception is raised when a connection attempt times out. It indicates that the service did not respond within the specified time frame.
- `socket.error`: This exception is raised for various socket-related errors, such as connection refusals or network issues. It can indicate that the service is not running or that there are network problems preventing a successful connection.
- 'ConnectionRefusedError': This exception is raised when a connection attempt is refused by the target service. It indicates that the service is not accepting connections on the specified port.
- `OSError`: This exception is raised for various operating system-related errors, such as permission issues or resource limitations. It can indicate that there are problems with the local system that are preventing the scanner from functioning properly.

## Why `connect_ex()` helps error handling?
The `connect_ex()` method is a non-blocking version of the `connect()` method in the socket library. It allows us to attempt a connection to a service without blocking the execution of our scanner. This means that if a connection attempt fails, we can handle the error gracefully without crashing the scanner or getting stuck. The `connect_ex()` method returns an error code instead of raising an exception, which allows us to easily check for specific error conditions and log them accordingly.

## Real-world limitations of banner Grabbing
While banner grabbing can be a useful technique for identifying services, it has several limitations in real-world scenarios. Some of these limitations include:
- banners can be hidden
- services can spoof responses
- firewalls may interfere with banner grabbing
- encrypted services may not provide banners

The real world limitations of banner grabbing highlight the importance of using multiple techniques for service detection and not relying solely on banners for identifying services. It also emphasizes the need for robust error handling in our scanner to account for these limitations and ensure that we can still gather valuable information about the services running on the target system.

## Security implications
While banner grabbing can provide valuable information about the services running on a target system, it can also have security implications. Attackers can use banner grabbing to gather information about the services running on a target system, which can help them identify potential vulnerabilities and plan their attacks. Therefore, it is important to implement proper security measures to protect against unauthorized banner grabbing, such as configuring services to hide or obfuscate their banners, implementing firewall rules to restrict access to certain ports, and regularly updating and patching services to mitigate known vulnerabilities. 

## Problems encountered during development
During the development of our scanner, we encountered several challenges related to service detection and error handling.
- **Scanner handling on `recv()`**: I had to ensure that the scanner could handle cases where the `recv()` method did not receive a response from the service. This required implementing proper error handling to prevent the scanner from crashing or getting stuck.

```python
try:
    banner = scanner.recv(1024).decode(errors="ignore").strip() 
    service = services.get(port, "Unknown")
    print(f"{port:<8}{service:<12}{'Open':<10}{banner}")
    open_ports.put({"port": port, "service": service, "banner": banner})
except socket.timeout:
    if port == 23:  
        print(f"{port:<8}{'Telnet':<12}{'Open':<10}{'No banner was received'}")
        open_ports.put({"port": port, "service": "Telnet", "banner": None})
    else:
        print(f"{port:<8}{'Unknown':<10}{'Open':<10}{'No banner was received'}")
        open_ports.put({"port": port, "service": "Unknown", "banner": None})
```
- **HTTP requirung explicit requests**: I had to implement specific HTTP requests to identify web servers, which required understanding the HTTP protocol and crafting appropriate requests to elicit responses that could help identify the service.

```python
if port == 80:
    request = "HEAD / HTTP/1.1\r\nHost: {}\r\n\r\n".format(target)
    try:
        scanner.send(request.encode())
    except (socket.error, ConnectionRefusedError, OSError):
        print(f"Failed to send HTTP request to port {port}.")
        return
```
- **Telnet authentication**: I had to account for the fact that some services, such as Telnet, may require authentication before providing a banner. This required implementing logic to handle cases where a banner was not received and providing appropriate output to indicate that the service is open but no banner was received.

- **Decoding problems**: I had to handle cases where the response from the service could not be decoded properly, which required using error handling to ignore decoding errors and ensure that the scanner could still function without crashing.

- **Timeout confusion**: I had to ensure that the scanner could handle timeouts properly, which required implementing logic to catch timeout exceptions and provide appropriate output to indicate that the service is open but no banner was received.

## Future improvements
In the future, I plan to implement additional techniques for service detection, such as:
- **Advances fingerprinting**: Implementing more advanced fingerprinting techniques that analyze the behavior of services to identify them, even when banners are not available.
- **TLS inspection**: Implementing TLS inspection to identify services that use encrypted communication, which may not provide banners.
- **Protcol-aware probing**: Implementing protocol-aware probing that sends specific requests based on the expected behavior of certain services to elicit responses that can help identify them.
- **Regex-based service identification**: Implementing regex-based service identification that analyzes the responses from services using regular expressions to identify patterns that can indicate the type of service running on an open port.
- **Integration with packet analysis tools**: Integrating the scanner with packet analysis tools to capture and analyze network traffic for more accurate service detection and identification. This can help identify services that may not provide banners or respond to specific requests, but can be identified through their network behavior.
- **Machine learning for service identification**: Implementing machine learning algorithms to analyze the responses from services and identify patterns that can indicate the type of service running on an open port. This can help improve the accuracy of service detection and identification, especially in cases where banners are not available or may be misleading.


**`To summarize, while banner grabbing can be a useful technique for identifying services, it has limitations and should be used in conjunction with other techniques for more accurate service detection. Implementing robust error handling is crucial to ensure that the scanner can continue functioning even when encountering network errors or services that do not provide banners. Future improvements can further enhance the capabilities of the scanner and improve its accuracy in identifying services running on open ports.`**


