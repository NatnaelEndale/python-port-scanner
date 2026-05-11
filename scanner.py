from os import scandir
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import socket
import json

target = "192.168.1.1"
open_ports = Queue()
services = {
    20: "FTP",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP",
    68: "DHCP",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB"
}

def port_scanner(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as scanner: 
        
        scanner.settimeout(0.5)
        result = scanner.connect_ex((target, port))
        
        if result == 0:
            scanner.settimeout(1.5)
            if port == 80:
                request = "HEAD / HTTP/1.1\r\nHost: {}\r\n\r\n".format(target)
                scanner.send(request.encode())
            try:
                banner = scanner.recv(1024).decode().strip() 
                service = services.get(port, "Unknown")
                print(f"Port {port} is open, Service: {service}, Banner: {banner}")
                open_ports.put({"port": port, "service": service, "banner": banner})
            except socket.timeout:
                if port == 23:  
                    print(f"Port {port} is open, Telnet service detected, but no banner was received.")
                    open_ports.put({"port": port, "service": "Telnet", "banner": None})
                else:
                    print(f"Port {port} is open, but no banner was received.")
                    open_ports.put({"port": port, "service": "Unknown", "banner": None})


if __name__ == "__main__":
    print(f"Scanning {target}...\n") 

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(port_scanner, range(1, 1025))


    print("\nScanning completed.")

    socan_results = []

    while not open_ports.empty():
        socan_results.append(open_ports.get())

    with open("report.json", "w") as file:
        json.dump(socan_results, file, indent=4)
    print("Report saved to report.json")
        

   

   # what does the port 23 and 22 do?
   # Port 22 is used for SSH (Secure Shell) which allows secure remote login and command execution on a remote machine. Port 23 is used for Telnet, which is an older protocol for remote login and command execution, but it is not secure and is generally not recommended for used due to security vulnerabilities.

# why we use the with keyword here?
         # The with keyword is used to create a context manager that automatically handles the setup and teardown of resources. In this case, it ensures that the socket is properly closed after the block of code is executed, even if an error occurs. This helps prevent resource leaks and ensures that the socket is released back to the system when it's no longer needed.
    # what does this line do?
         # This line attempts to receive data from the socket after a successful connection. It reads up to 1024 bytes of data, decodes it from bytes to a string, and then removes any leading or trailing whitespace. This is often used to capture the banner information from a service running often on the open port, which can provide information about the service and its version.    

