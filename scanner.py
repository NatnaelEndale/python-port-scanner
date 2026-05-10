from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import socket
import errno
import json

target = "192.168.1.1"
open_ports = Queue()

def port_scanner(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as scanner: 
        
        scanner.settimeout(0.5)
        result = scanner.connect_ex((target, port))
        
        if result == 0:
            if port == 80:
                request = "HEAD / HTTP/1.1\r\nHost: {}\r\n\r\n".format(target)
                scanner.send(request.encode())
            try:
                banner = scanner.recv(1024).decode().strip() 
                match port:
                    case 20 | 21:
                        print(f"Port {port} is open, FTP service detected: {banner}")
                        open_ports.put({"port": port, "service": "FTP", "banner": banner})
                    case 22:
                        print(f"Port {port} is open, SSH service detected: {banner}")
                        open_ports.put({"port": port, "service": "SSH", "banner": banner})
                    case 23:
                        print(f"Port {port} is open, Telnet service detected: {banner}")
                        open_ports.put({"port": port, "service": "Telnet", "banner": banner})
                    case 25:
                        print(f"Port {port} is open, SMTP service detected: {banner}")
                        open_ports.put({"port": port, "service": "SMTP", "banner": banner})
                    case 53:
                        print(f"Port {port} is open, DNS service detected: {banner}")
                        open_ports.put({"port": port, "service": "DNS", "banner": banner})
                    case 67 | 68:
                        print(f"Port {port} is open, DHCP service detected: {banner}")
                        open_ports.put({"port": port, "service": "DHCP", "banner": banner})
                    case 80:
                        print(f"Port {port} is open, HTTP service detected: {banner}")
                        open_ports.put({"port": port, "service": "HTTP", "banner": banner})
                    case 110:
                        print(f"Port {port} is open, POP3 service detected: {banner}")
                        open_ports.put({"port": port, "service": "POP3", "banner": banner})
                    case 143:
                        print(f"Port {port} is open, IMAP service detected: {banner}")
                        open_ports.put({"port": port, "service": "IMAP", "banner": banner})
                    case 443:
                        print(f"Port {port} is open, HTTPS service detected: {banner}")
                        open_ports.put({"port": port, "service": "HTTPS", "banner": banner})
                    case 445:
                        print(f"Port {port} is open, SMB service detected: {banner}")
                        open_ports.put({"port": port, "service": "SMB", "banner": banner})

            except:
                if port == 23:  
                    print(f"Port {port} is open, Telnet service detected, but no banner was received.")
                    open_ports.put({"port": port, "service": "Telnet", "banner": None})
                else:
                    print(f"Port {port} is open, but no banner was received.")
                    open_ports.put({"port": port, "service": "Unknown", "banner": None})
        elif result == errno.ECONNREFUSED:
            print(f"Port {port} is closed.")
        elif result == errno.ETIMEDOUT:
            print(f"Port {port} is filetered.")
        elif result == errno.EHOSTUNREACH:
            print(f"Port {port} is host unreachable.")

if __name__ == "__main__":
    print(f"Scanning {target}...\n") 

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(port_scanner, range(1, 1025))

    print("\nScanning completed.")
    print(f"Open ports: {list(open_ports.queue)}")

   

   # what does the port 23 and 22 do?
   # Port 22 is used for SSH (Secure Shell) which allows secure remote login and command execution on a remote machine. Port 23 is used for Telnet, which is an older protocol for remote login and command execution, but it is not secure and is generally not recommended for used due to security vulnerabilities.

# why we use the with keyword here?
         # The with keyword is used to create a context manager that automatically handles the setup and teardown of resources. In this case, it ensures that the socket is properly closed after the block of code is executed, even if an error occurs. This helps prevent resource leaks and ensures that the socket is released back to the system when it's no longer needed.
    # what does this line do?
         # This line attempts to receive data from the socket after a successful connection. It reads up to 1024 bytes of data, decodes it from bytes to a string, and then removes any leading or trailing whitespace. This is often used to capture the banner information from a service running often on the open port, which can provide information about the service and its version.    

