# Python Concurrent Port Scanner

A multithreaded TCP port scanner built in Python for network reconnaissance and cybersecurity learning purposes.

This project demonstrates practical understanding of:

* TCP socket programming
* Concurrent network scanning
* Banner grabbing
* Service identification
* CLI application design
* JSON report generation
* Error handling in network applications

---

# Features

* Concurrent TCP port scanning using `ThreadPoolExecutor`
* Configurable port ranges
* Banner grabbing for service fingerprinting
* Basic HTTP probing for web servers
* JSON scan report generation
* Timestamped scan reports
* Input validation for targets and port ranges
* Command-line interface with subcommands
* Scan summary output
* Structured terminal output

---

# Technologies Used

* `Python 3`
* `socket`
* `concurrent.futures`
* `argparse`
* `json`
* `queue`
* `Multithreading`

---

# How It Works

The scanner performs a TCP Connect Scan by attempting to establish TCP connections to target ports.

If a port accepts the connection:

1. The port is marked as open
2. The scanner attempts banner grabbing
3. Known services are identified using common port mappings
4. Results are saved into a structured JSON report

The scanner uses multithreading to improve performance and scan multiple ports concurrently.

---

# Project Structure

```bash
scanner.py
report.json
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/python-port-scanner.git
cd python-port-scanner
```

No external dependencies are required.

---

# Usage

## Scan a Target

```bash
python scanner.py scan 192.168.1.1
```

---

## Scan Specific Port Range

```bash
python scanner.py scan 192.168.1.1 --range 1 500
```

---

## View Report

```bash
python scanner.py report
```

---

# Example Output

```text
PORT    SERVICE    STATUS    BANNER
------------------------------------------------------------
22      SSH         Open      SSH-2.0--
23      Telnet      Open      Login authentication
80      HTTP        Open      Apache/2.4.58
```

---

# Example JSON Report

```json
{
   "target": "192.168.1.1",
   "scan_time": "2026-05-12T15:20:41",
   "duration_seconds": 3.42,
   "results": [
      {
         "port": 22,
         "service": "SSH",
         "banner": "SSH-2.0--"
      },
      {
         "port": 23,
         "service": "Telnet",
         "banner": "Login authentication"
      }
   ]
}
```

---

# Error Handling

The scanner includes handling for:

* Connection timeouts
* Invalid targets
* Invalid port ranges
* Socket errors
* Banner decoding issues
* HTTP request failures

---

# Learning Objectives

This project was built to strengthen understanding of:

* Network communication fundamentals
* TCP/IP concepts
* Concurrent programming in Python
* Thread pools and synchronization
* Socket timeouts and blocking I/O
* Network reconnaissance techniques

---

# Limitations

This scanner currently performs:

* TCP Connect Scanning only

It does not currently support:

* SYN scanning
* UDP scanning
* OS fingerprinting
* Advanced service fingerprinting
* SSL/TLS inspection

---

# Future Improvements

Possible future enhancements:

* SYN scanning using raw packets
* UDP scanning
* Service fingerprinting improvements
* Colored terminal output
* Export formats (CSV/XML)
* Improved HTTP/HTTPS detection
* Asynchronous scanning using `asyncio`

---

# Disclaimer

This project is intended for:

* Educational purposes
* Authorized network testing
* Cybersecurity learning

Do not scan systems you do not own or have permission to test.

---

# Author

Natnael (Natty)

Passionate about cybersecurity, networking, and secure systems engineering.

