# CSA07 – Computer Networks | Assignment 3 (CO3)

**Student:** S. Sofiya  
**Register Number:** 192521248  
**Repository:** `CSA07-192521248-Assignment3`

## Environment
- OS: Windows (edit if different)
- Python: 3.x
- Wireshark: enter installed version
- Packet Tracer / simulator: enter version if used

## Contents
- `answers.md` – worked answers for Q1–Q7
- `Task01/` – TCP/UDP socket server and client
- `Task02/` – TCP Tahoe/Reno congestion-window simulation
- `Task03/` – HTTP timing calculations
- `Task04/` – iterative DNS cache simulation
- `Task05/` – M/M/1 queue calculations and plot program
- `Task06/` – handshake timing comparison
- `Task07/` – telemedicine protocol design and socket examples

## Run programs
From the extracted repository folder:
```bash
python Task01/socket_lab.py
python Task02/congestion.py
python Task04/dns_simulation.py
python Task05/mm1.py
python Task06/handshake.py
python Task07/file_server.py
```
Python programs use the standard library except the optional plot script, which requires `matplotlib`.

## Evidence you must create
The assignment requires individual execution and evidence. Run the programs yourself and add terminal screenshots/output. For Q1, capture loopback traffic in Wireshark and mark the TCP three-way handshake and UDP datagrams. For Q2, run the `iperf3`/`ss -ti`/`tc netem` experiments if available. For Q3, use browser Developer Tools and record h1/h2/h3, connections and load times. For Q4, run `dig +trace` and compare public DNS resolvers. For Q5, capture queue/QoS tests. For Q6, capture TLS 1.3 and test HTTP/3 support. For Q7, test file transfer and chat under delay/loss.

Do not claim a capture, measurement, or experiment was completed until you have run it. Add actual PCAPs, screenshots and measured values in the relevant task folders.

## GitHub
1. Extract the ZIP.
2. Create a repository named `CSA07-192521248-Assignment3`.
3. Upload the extracted files.
4. Make progressive commits, ideally one commit per task as required by the assignment.
5. Replace `YOUR-USERNAME` below with your GitHub username:
```bash
git init
git add .
git commit -m "Add CO3 assignment answers and starter programs"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/CSA07-192521248-Assignment3.git
git push -u origin main
```
