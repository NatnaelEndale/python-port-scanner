from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import socket
import json
import argparse
from json.decoder import JSONDecodeError
from itertools import repeat
from datetime import datetime

REPORT_FILE = "report.json"
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

def port_scanner(port, target):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as scanner: 
        
        scanner.settimeout(0.5)
        try:
            result = scanner.connect_ex((target, port))
        except socket.error:
            print(f"Failed to connect to port {port}.")
            return
        
        if result == 0:
            scanner.settimeout(1.5)
            if port == 80:
                request = "HEAD / HTTP/1.1\r\nHost: {}\r\n\r\n".format(target)
                try:
                    scanner.send(request.encode())
                except (socket.error, ConnectionRefusedError, OSError):
                    print(f"Failed to send HTTP request to port {port}.")
                    return 
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


def see_report():
    with open(REPORT_FILE, "r") as f:
        try:
            report = json.load(f)
            print(json.dumps(report, indent=3))
        except JSONDecodeError:
            print("Report file is empty or contains invalid JSON.")

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

def summary(p_range, scan_results, duration_seconds):
    print(f"Scanning ports from {p_range[0]} to {p_range[1]}...")
    num_open_ports = len(scan_results)
    print(f"{num_open_ports} open ports found.")
    print(f"Duration: {duration_seconds:.2f} seconds")



def scan(target, p_range):
    if validate_target(target) and validate_port_range(p_range):
        target = socket.gethostbyname(target)
        print(f"Scanning {target}...\n")
        print(f"\n\n{'PORT':<8}{'SERVICE':<12}{'STATUS':<10}{'BANNER':<30}")
        print("-" * 60)

        start_time = datetime.now()

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(port_scanner, range(p_range[0], p_range[1] + 1), repeat(target))

        print("\nScanning completed.")

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
        print(f"Report saved to {file_name}")

        print("\nScan Summary:")
        summary(p_range, scan_results, duration_seconds)
        return final_report
    else:
        print("Please provide a valid IP address or hostname. or Invalid port range. Please provide a valid range between 1 and 65535.")



def main():
    parser = argparse.ArgumentParser(description="A Port Scanner.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    scan_parser = subparsers.add_parser("scan", help="Perform a port scan on the specified target.")
    scan_parser.add_argument("target", help="Target IP address to scan.")
    scan_parser.add_argument("--range", nargs=2, type=int, default=[1, 1024], help="Port range to scan (e.g., 1-1024).")

    subparsers.add_parser("report", help="View the scan report.")

    args = parser.parse_args()

    if args.command == "scan":
        scan(args.target, args.range)

    elif args.command == "report":
        see_report()



if __name__ == "__main__":
    main()
   
        

   


