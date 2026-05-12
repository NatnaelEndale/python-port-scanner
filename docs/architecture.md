# Architecture
The scanner performs concurrent TCP connect scans against a target host,
attempting to identify open ports and gather service banners.

## The Scanner simply does this
User CLI Input<\br>
       │<\br>
       ▼<\br>
Argument Parsing (argparse)<\br>
       │<\br>
       ▼<\br>
Validation Layer<\br>
       │<\br>
       ▼<\br>
ThreadPoolExecutor<\br>
       │<\br>
       ▼<\br>
Port Scanner Workers<\br>
       │<\br>
       ▼<\br>
Banner Grabbing & Service Detection<\br>
       │<\br>
       ▼<\br>
Queue Collection<\br>
       │<\br>
       ▼<\br>
JSON Report Generation

## CLI Layer 
The CLI layer is responsible for parsing user input and validating it. It uses the `argparse` library to handle command-line arguments, ensuring that the user provides valid IP addresses, port ranges, and other necessary parameters. 

### argparse:
argparse is a powerful library that allows for easy handling of command-line arguments, providing built-in validation and help messages. It ensures that the user input is correctly formatted and meets the expected criteria before proceeding with The scanning process.


### subparsers:
Subparsers allow for the creation of multiple subcommands within a single CLI application. This is useful for organizing different functionalities or modes of operation, such as scanning, reporting, or configuration management. Each subcommand can have its own set of arguments and options, making the CLI more flexible and user-friendly.

```python
parser = argparse.ArgumentParser(description="A Port Scanner.") 
subparsers = parser.add_subparsers(dest="command", help="Available commands")
```

### Command Separation
The scanner separtes the command `sacn` and `report` into two different subcommands. This allows for a clear distinction between the scanning process and the reporting process, making the tool more organized and easier to use.

## Validation layer
The validation layer ensures that the user input is valid before proceeding with the scanning process. It checks for valid IP addresses, port ranges, and other necessary parameters. This layer helps prevent errors and ensures that the scanner operates on valid targets.

### Hostname responsible
The hostname responsible for validating the target host input, ensuring that it is a valid IP address or domain name. It uses `socket.getbyhostname(target)` from the socket library to perform this validation.

### Port Range validation
The port range validation ensures that the user provides a valid range of ports to scan. It checks that the start and end ports are within the acceptable range (1-65535) and that The start port is less than or equal to the end port.

### why invalid input should fail early
Failing early on invalid input is crucial for several reasons:
1. **User Experience**: Providing immediate feedback on invalid input helps users understand what went wrong and how to correct it, improving the overall user experience.
2. **Resource Efficiency**: its prevents the scanner from wasting resources on attempting to scan invalid targets or port ranges, which can lead to faster execution and reduced system load.
3. **Security**: Validating input early can help prevent potential security vulnerabilities, such as injection attacks or unintended behavior caused by malformed input.

## Concurrency Architecture
The scanner utilizes a concurrent architecture to perform TCP connect scans efficiently. It employs the `ThreadPoolExecutor` from the `concurrent.futures` module to manage a pool of worker threads that performs the scanning tasks concurrently.

### Why sequential scanning is inefficient
Sequential scanning can be inefficient because it processes one port at a time, which can be time-consuming, especially when scanning a large range of ports. Each connection attempt may take several seconds to timeout if the port is closed, leading to a significant delay in completing the scan.

### Why thread pools were chosen
Thread pools were chosen for their ability to manage a large number of concurrent tasks without the overhead of creating and destroying threads for each task. They allow for efficient use of system resources while maintaining responsiveness and scalability. The `ThreadPoolExecutor` provides a simple and effective way to handle concurrent scanning tasks, allowing the scanner to perform multiple scans simultaneously, reuse threads and significantly reduce the overall scanning time.

### I/O-bound concurrent
The scanning process is I/O-bound because it involves waiting for network responses from the target host. Using a thread pool allows the scanner to perform multiple scans concurrently, maximizing the use of available threads while waiting for responses, and improving the overall efficiency of the scanning process.

### worker model
The worker model involves creating a pool of worker threads `ThreadPoolExecutor` that perform scanning tasks concurrently. Each worker thread is responsible for scanning a specific port on the target host, attempting to establish a TCP connection and gather service banners if the port is open. The results from each worker thread are collected in a queue, which is then used to generate the final report. This model allows for efficient handling of multiple scanning tasks while maintaining responsiveness and scalability.

## Scanning Workflow
The scanning workflow(Lifecyle) involves several steps:
1. **Configure timeout**: The scanner sets a timeout for each connection attempt to prevent hanging on unresponsive ports.

```python
scanner.settimeout(timeout)
```

2. **Attempt TCP connection**: The worker thread attempts to establish a TCP connection to the target host on the specified port.

```python
try:
    result = scanner.connect_ex((target, port))
except socket.error:
    print(f"Failed to connect to port {port}.")
    return
    ```

3. **Identify open ports**: If the connection is successful (result == 0), the port is identified as open, and the scanner proceeds to gather service banners.
```python
if result == 0:
    scanner.settimeout(timeout)
```

4. **Send optional protocol probes**: The scanner may send protocol-specific probes (e.g., HTTP, FTP) to gather more information about the service running on the open port.

```python
if port == 80:
    request = "HEAD / HTTP/1.1\r\nHost: {}\r\n\r\n".format(target)
```

5. **Receive banner**: The scanner attempts to receive a banner from the open port, which may contain information about the service and its version, stores the info in dictionary and prints the structured output.

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
        open_ports.put({"port": port, "service": "Unknown", "banner": None})```

6. **Store results**: The results from each worker thread are stored in a queue, which is later used to generate a JSON report summarizing the scan results.

```python
open_ports.put({"port": port, "service": service, "banner": banner})
...
scan_results = []

    while not open_ports.empty():
        scan_results.append(open_ports.get())

    duration_seconds = (datetime.now() - start_time).total_seconds() if scan_results else 0
    final_report = {
            "target": target,
            "scan_time": datetime.now().isoformat(),
            "duration_seconds": duration_seconds,
            "results": scan_results
            }
    file_name = f"scan_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json"

    with open(file_name, "w") as file:
        json.dump(final_report, file, indent=3)
    print("Report saved to report.json")
```

## Socket Design
The scanner uses the `socket` library to perform TCP connections and gather service banners. The Socket design involves creating a socket object for each worker thread, configuring it with a timeout, and using it to attempt connections to the target host on specified ports. The socket is also used to send protocol-specific probes and receive banners from open ports. The socket design allows for efficient handling of network communication, enabling the scanner to perform concurrent scans and gather detailed information about the services running on open ports.

### `AF_INET` and `SOCK_STREAM`
The scanner uses `AF_INET` to specify that it is working with IPv4 addresses and `SOCK_STREAM` to indicate that it is using TCP for communication. This combination allows the scanner tool to establish reliable connections to the target host and gather information about open ports and services effectively.

```python
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as scanner:
```

### TCP sockets
TCP sockets provide a reliable, connection-oriented communication channel between the scanner and the target host. This allows the scanner to establish a connection, send probes, and receive banners without worrying about packet loss or ordering issues, making it an ideal choice for port scanning and service detection tasks.

### Blocking I/O
The scanner uses blocking I/O for socket operations, which means that the worker thread will wait for the connection attempt to complete or timeout before proceeding. This is suitable for the scanning process, as it allows the scanner to handle each connection attempt sequentially within each worker thread while still benefiting from the Concurrency provided by the thread pool. Blocking I/O simplifies the implementation and ensures that the scanner can effectively manage multiple concurrent scans without the complexity of non-blocking I/O or asynchronous programming.

### Timeouts
The scanner sets a timeout for each socket operation to prevent hanging on unresponsive ports. This ensures that the scanner can efficiently move on to the next port if a connection attempt takes too long, improving the overall scanning speed and responsiveness. Timeouts are crucial for handling cases where ports are closed or filtered, allowing the scanner to avoid getting stuck and ensuring that it can complete the scan in a reasonable amount of time.

```python
scanner.settimeout(0.5)
scanner.settimeout(1.5)
```

## Banner Grabbing Logic
The banner grabbing logic is responsible for sending protocol-specific probes to open ports and receiving banners that may contain information about the service and its version. The scanner sends probes based on common ports (e.g., HTTP on port 80) to elicit responses from the services running on those ports. If a banner is received, it is decoded and stored in a structured format for reporting. If no banner is received within the timeout period, the scanner handles this gracefully by indicating that no banner was received while still marking the port as open. This logic allows the scanner to gather valuable information about the services running on open ports, enhancing the overall effectiveness of the scan.

```python
try:
    banner = scanner.recv(1024).decode(errors="ignore").strip()
```

### Passive Banners (SSH/Telnet)
For services like SSH and Telnet, which often provide a banner immediately upon connection, the scanner attempts to receive this banner without sending any probes. If a banner is received, it is decoded and stored. If no banner is received within the timeout period, the scanner handles this case by indicating that no banner was received while still marking the port as open, especially for Telnet where a banner may not always be provided.

### Active probing (HTTP)
For services like HTTP, the scanner sends a specific probe (` request = "HEAD / HTTP/1.1\r\nHost: {}\r\n\r\n".format(target)`) to elicit a response from the server. This allows the scanner to gather more detailed information about the service, such as the server software and version, which may be included in the response headers.

### Protocol behavior defferences
Different protocols have different behaviors when it comes to banner grabbing. For example, HTTP servers typically respond to specific requests with detailed information in the headers, while SSH and Telnet servers may provide a banner immediately upon connection. The scanner's banner grabbing logic accounts for these differences by using protocol-specific probes and handling the responses accordingly, ensuring that it can effectively gather information from a variety of services running on open ports.

### Queue-Based Result Collection
The scanner uses a queue to collect results from worker threads. Each worker thread puts its results (port, service, banner) into the queue, which is then processed after all threads have completed their tasks. This approach allows for thread-safe communication between worker threads and the main thread, ensuring that results are collected efficiently without the need for complex synchronization mechanisms. The queue-based result collection simplifies the aggregation of scan results and facilitates the generation of a structured report at the end of the scanning process.

```python
open_ports = Queue()
#...
open_ports.put({"port": port, "service": service, "banner": banner})
```

### thread-safe communication
Using a queue for result collection ensures thread-safe communication between worker threads and the main thread. The `Queue` class from the `queue` module provides built-in synchronization mechanisms that allow multiple threads to safely add and retrieve items without the risk of data corruption or race conditions. This allows the scanner to efficiently collect results from concurrent worker threads while maintaining the integrity of the data and ensuring that the final report accurately reflects the scan results.

### Shared data
The scanner uses a shared data structure (the queue) to collect results from worker threads. This allows for efficient communication and aggregation of results without the need for complex synchronization mechanisms. The shared data structure enables the main thread to easily access and process the results collected by the worker threads, facilitating the generation of a comprehensive report at the end of the scanning process.

### synchronization
The `Queue` class provides built-in synchronization mechanisms that allow multiple threads to safely add and retrieve items without the risk of data corruption or race conditions. This ensures that the scanner can efficiently collect results from concurrent worker threads while maintaining the integrity of the data and ensuring that the final report accurately reflects the scan results. The use of a queue simplifies the synchronization process, allowing the scanner to focus on its core functionality without worrying about thread safety issues.

## Reporting System
The reporting system is responsible for generating a structured report based on the results collected from the worker threads.

### JSON structure
The report is generated in JSON format, which provides a structured and easily readable representation of the scan results. The JSON structure includes information about the target, scan time, duration, and a list of results for each open port, including the port number, service name, and banner information. This structured format allows for easy parsing and analysis of the scan results, making it suitable for further processing or integration with other tools.

```json
{
   "target": "192.168.1.1",
   "scan_time": "2026-05-12T16:07:16.998231",
   "duration_seconds": 5.027373,
   "results": [
      {
         "port": 22,
         "service": "SSH",
         "banner": "SSH-2.0--"
      },
      {
         "port": 23,
         "service": "Telnet",
         "banner": "Warning: Telnet is not a secure protocol, and it is recommended to use Stelnet.\r\n\r\nLogin authentication\r\n\r\n\r\nUsername:\u0001\u0001\u0001"
      }
   ]
}
```
### Scan Summaries
The report includes a summary of the scan, such as the target, scan time, and duration. This information provides context for the scan results and allows users to understand when the scan was performed and how long it took to complete.

```
Scan Summary:
Scanning ports from 1 to 100...
2 open ports found.
Duration: 5.03 seconds
```
## Error Handling Strategy
The scanner implements error handling strategies to manage potential issues that may arise during the scanning process. This includes handling socket errors, timeouts, and invalid input.

### timeouts
The scanner sets timeouts for socket operations to prevent hanging on unresponsive ports. If a connections attempt takes too long, the scanner will move on to the next port, ensuring that the scan can complete in a reasonable amount of time.

### socket failures
The scanner handles socket errors gracefully by catching exceptions and providing informative messages to the user. This ensures that the scanner can continue operating even if it encounters issues with specific ports or network conditions, improving the overall robustness of the tool.

### invalid input
The scanner validates user input at the CLI layer, ensuring that it is correctly formatted and meets the expected criteria before proceeding with the scanning process. If the user provides invalid input, the scanner will provide immediate feedback and prevent the scan from starting, improving the user experience and preventing potential issues during the scanning process.

### Network unpredictability
The scanner is designed to handle the unpredictability of network conditions, such as packet loss, latency, and varying response times. By using timeouts and error handling strategies, the scanner can effectively manage these conditions and ensure that the scanning process remains efficient and reliable, even in less-than-ideal network environments. This allows the scanner to provide accurate results while minimizing the impact of network issues on the overall scanning process.

```python
def validate_target(target):
    try:
        socket.gethostbyname(target)
        return True
    except socket.error:
        return False

def validate_port_range(port_range):
    if len(port_range) != 2:
        return False
    try:
        start_port = int(port_range[0])
        end_port = int(port_range[1])
        if 1 <= start_port <= 65535 and 1 <= end_port <= 65535 and start_port <= end_port:
            return True
        else:
            return False
    except ValueError:
        return False
```

## Design Decisions
1. **connect_ex() instead of connect()**: The scanner uses `connect_ex()` instead of `connect()` to attempt TCP connections. This method returns an error code instead of raising an exception, allowing the scanner to handle connection attempts more gracefully and efficiently without the overhead of exception handling for each failed connection.

2. **ThreadPoolExecutor for concurrency**: The scanner uses `ThreadPoolExecutor` to manage a pool of worker threads for concurrent scanning. This design choice allows for efficient handling of multiple scanning tasks while maintaining responsiveness and scalability, significantly reducing the overall scanning time compared to sequential scanning.

3. **Queue for result collection**: The scanner uses a `Queue` to collect results from worker threads. This design choice ensures thread-safe communication between worker threads and the main thread, allowing for efficient aggregation of results without the need for complex synchronization mechanisms.

4. **JSON for reporting**: The scanner generates reports in JSON format, providing a structured and easily readable representation of the scan results. This design choice allows for easy parsing and analysis of the results, making it suitable for further processing or integration with other tools.

5. **Timeouts for socket operations**: The scanner sets timeouts for socket operations to prevent hanging on unresponsive ports. This design choice ensures that the scanner can efficiently move on to the next port if a connection attempt takes too long, improving the overall scanning speed and responsiveness.

## Limitations

1. **TCP connection scanning only**: The scanner is limited to performing TCP connect scans and does not support other types of scans (e.g., SYN scan, UDP scan), which may provide different insights into the target's network.

2. **no advanced fingerprinting**: The scanner relies on basic banner grabbing for service detection and does not implement advanced fingerprinting techniques that could provide more detailed information about the services running on open ports.

3. **no TLS analysis**: The scanner does not analyze TLS/SSL certificates or perform any checks related to encrypted services, which could provide additional information about the target's security posture.

## Future Enhancements
1. **raw socket support**: Implementing raw socket support would allow the scanner to perform more advanced scanning techniques, such as SYN scans or UDP scans, providing a more comprehensive view of the target's network.

2. **async Scanning**: Implementing asynchronous scanning using libraries like `asyncio` could further improve the efficiency of the scanner, allowing it to handle a larger number of concurrent scans without the overhead of thread management.

3. **Service fingerprinting**: Implementing advanced service fingerprinting techniques could provide more detailed information about the services running on open ports, enhancing the overall effectiveness of the scan.

4. **Scapy integration**: Integrating with the `Scapy` library could allow for more flexible and powerful packet crafting and analysis, enabling the scanner to perform a wider range of scanning techniques and gather more detailed information about the target's network.
