# CSA07 – Computer Networks | Assignment 3 – CO3
**Student:** S. Sofiya | **Register Number:** 192521248

## Q1 – Which Socket Gets the Segment?

### 1. Socket demultiplexing

| Arriving segment | Receiving socket | Reason |
|---|---|---|
| TCP from 49.37.2.8:50001 to server port 443 | Established TCP connection `203.0.113.5:443 <-> 49.37.2.8:50001` | Exact connection tuple matches |
| TCP from 117.96.4.2:50000 to server port 443 | Established TCP connection `203.0.113.5:443 <-> 117.96.4.2:50000` | Exact connection tuple matches |
| TCP SYN from 106.51.7.7:41000 to server port 443 | TCP listening socket `203.0.113.5:443` | New connection; no established tuple exists |
| UDP from 49.37.2.8:50000 to server port 5004 | UDP socket `203.0.113.5:5004` | UDP demultiplexing uses destination port/local address; one socket can receive datagrams from many sources |

Two TCP connections can use the same client source port 50000 because their remote IP addresses differ. A TCP connection is identified by the four-tuple (source IP, source port, destination IP, destination port). The single UDP socket on port 5004 can receive packets from many viewers, but the application must inspect the source address returned with each datagram to distinguish them; the local port alone does not identify a viewer.

### 2. Header overhead for 100-byte application data (IPv4, no options)
- UDP: 20-byte IPv4 header + 8-byte UDP header = 28 bytes overhead. Overhead relative to 100-byte payload = 28/100 × 100 = **28%**.
- TCP: 20-byte IPv4 header + 20-byte minimum TCP header = 40 bytes overhead. Overhead relative to 100-byte payload = 40/100 × 100 = **40%**.

### 3. App protocol choice
- Live score updates: UDP can be suitable when freshness matters more than retransmission; stale score packets can be ignored, but application-level sequence/timestamp handling is useful.
- Ball-by-ball commentary: TCP/HTTPS is suitable because complete, ordered text delivery matters.
- Live video: UDP-based media transport is usually preferred for low delay; lost frames may be concealed rather than waiting for retransmission. A reliable TCP-based stream can freeze during loss.

### 4. Completed Python socket program
See `Task01/socket_lab.py`. It implements the required UDP `recvfrom`/`sendto` echo and TCP receive loop. Expected output:
```text
UDP lab1 -> ACK:lab1
UDP lab2 -> ACK:lab2
UDP lab3 -> ACK:lab3
TCP server received 100000 bytes in order
```

### 5. TCP alternative for live video
At 500 packets/s and 2% loss, expected lost packets per minute = 500 × 60 × 0.02 = **600 packets/minute**. With 60 ms RTT, each loss can cause at least about one RTT (60 ms) of recovery delay, depending on congestion control, loss detection and buffering. If each lost packet causes a separate visible freeze, an upper simple estimate is 600 freeze events/minute; in practice losses may be grouped and playback buffering changes the number and duration. TCP head-of-line blocking can delay later data until missing bytes are recovered.

**Conclusion:** UDP is not “never use”; it is useful for real-time traffic that values timeliness. TCP is better when reliable, ordered delivery is required.

---

## Q2 – Read the Congestion Window

Given cwnd values by RTT: 1, 2, 4, 8, 16, 17, 18, 19, 9, 10, 11, 12, 13, 14, 1, 2, 4.

### 1. ssthresh and loss events
- Initial `ssthresh` = **16 segments** (slow start grows 1, 2, 4, 8, 16, then linear growth).
- At RTT 8, cwnd falls from 19 to 9 at RTT 9. New `ssthresh` is approximately floor(19/2) = **9**. This is consistent with a multiplicative decrease / fast-recovery response.
- At RTT 14, cwnd falls from 14 to 1 at RTT 15. A reset to 1 is consistent with a retransmission timeout / Tahoe-style response. If the loss threshold is calculated from the pre-loss cwnd, `ssthresh` becomes floor(14/2) = **7**.
- The trace shows Reno-like behaviour at the first loss and Tahoe/timeout-like reset at the second. It is not a pure single-behaviour trace. A graph alone suggests the response but cannot prove the exact packet-level loss signal; inspect duplicate ACKs and retransmission timing in Wireshark to confirm.

### 2. Throughput at RTT 7
At RTT 7, cwnd = 18 segments. Segment size = 1,460 bytes; RTT = 0.04 s.
Throughput = (18 × 1,460 × 8) / 0.04 = **52,560,000 bit/s = 52.56 Mbps** (ideal window-limited estimate).

### 3. Why AIMD shares fairly
Additive increase gives competing TCP flows similar linear growth. When congestion occurs, multiplicative decrease reduces each flow's rate proportionally. Over time, this tends toward a fair share when flows have similar RTTs and bottleneck conditions. Different RTTs and loss patterns can still create unfairness.

### 4. Tahoe/Reno code
See `Task02/congestion.py`. It follows the assignment's provided simplified model and prints both traces. Reno retains half-window after loss; Tahoe returns to cwnd 1.

### 5. CUBIC vs BBR
CUBIC is widely used for high-bandwidth, long-distance paths and grows its congestion window using a cubic function. BBR estimates bottleneck bandwidth and propagation RTT, so it can perform better when random non-congestion loss would unnecessarily reduce a loss-based sender's window. Under real congestion, BBR still needs appropriate queue control and fairness testing. Choose based on measured delay, loss type, throughput and fairness rather than assuming one is always best.

**Result:** Congestion-window thresholds, loss responses and ideal throughput were calculated.

---

## Q3 – Why Does the Home Page Take 8 Seconds?

RTT = 50 ms; one HTML file plus 80 small objects; transmission times negligible. Assume each new non-persistent TCP connection needs 1 RTT for TCP setup and 1 RTT for the HTTP request/response, and ignore DNS/TLS unless stated.

### 1. Page-load calculations
- Non-persistent HTTP, one connection at a time: HTML takes 2 RTT; 80 objects each take 2 RTT. Total = (1 + 80) × 2 × 50 ms = **8,100 ms = 8.1 s**.
- Persistent HTTP/1.1 without pipelining: initial HTML = 2 RTT; each of 80 objects = 1 RTT. Total = 82 RTT = **4.1 s**.
- Persistent HTTP/1.1 with pipelining: initial HTML = 2 RTT; all object requests pipelined and responses returned in approximately 1 further RTT. Total = 3 RTT = **150 ms** (idealised).
- Six parallel non-persistent connections: HTML first takes 2 RTT. 80 objects in batches of 6 require ceil(80/6) = 14 batches, each about 2 RTT. Total = (2 + 14×2) RTT = 30 RTT = **1.5 s**.

### 2. HTTP/2 and HTTP/3
HTTP/2 multiplexes streams over one TCP connection, but TCP delivers bytes in order. Loss of a TCP segment can hold up data for multiple streams until retransmission (transport head-of-line blocking). HTTP/3 uses QUIC over UDP with independent streams, so loss in one stream does not block delivery on unrelated streams in the same way.

### 3. Cache-Control and ETag
`Cache-Control: max-age=...` allows a browser to reuse a fresh cached object without contacting the server; the second visit can avoid the request/response RTT and object transfer for those fresh objects. `ETag` enables conditional requests (`If-None-Match`); if unchanged, the server returns 304 Not Modified, saving the body bytes but still requiring a network round trip. Exact time saved depends on cache lifetime, number of objects and validation strategy.

### 4. Bundle alternative
Combining 80 objects into 8 bundles:
- Non-persistent sequential: HTML + 8 bundles = 9 resources × 2 RTT = 18 RTT = **0.9 s**.
- Persistent HTTP/1.1 without pipelining: HTML 2 RTT + 8 bundle requests × 1 RTT = 10 RTT = **0.5 s**.
This reduces request/connection overhead. HTTP/2 may still improve multiplexing and prioritisation, but bundling can also reduce cache granularity.

**Engineering decision:** Enable caching, use HTTP/2 or HTTP/3 where supported, reduce object count and use a CDN/nearby edge. Measure on the actual mobile network before ranking final changes.

---

## Q4 – How Many Queries Reach the University’s DNS Server?

### 1. Queries per hour per resolver
With a cache, a resolver generally needs a fresh authoritative lookup after the cached TTL expires, assuming there is continuing demand.
- TTL 300 s: 3600/300 = **12 queries/hour per resolver**.
- TTL 30 s: 3600/30 = **120 queries/hour per resolver**.

For 40 independent resolvers, the simplified totals would be 40×12 = **480 queries/hour** at TTL 300 s, or 40×120 = **4,800 queries/hour** at TTL 30 s. The prompt says 40 cities, not necessarily exactly 40 resolvers; actual load depends on the number of ISP resolver caches and query patterns.

### 2. Why student count matters less
Many students behind the same recursive resolver share its cached DNS answer. The authoritative server mainly sees cache misses from recursive resolvers, so resolver count and TTL strongly affect its query rate. Student count affects load on recursive resolvers and may affect cache misses if demand is sparse or distributed.

### 3. Recursive vs iterative resolution
The phone sends a recursive query to its configured recursive resolver and expects a final answer. The resolver performs iterative lookups, following referrals:
1. Root server → referral to `.in` TLD servers.
2. `.in` TLD server → referral to `ac.in` name servers.
3. `ac.in` server → referral to `simats.ac.in` authoritative server.
4. Authoritative server → final A/AAAA answer.
The assignment's simplified code models four server queries for `results.simats.ac.in.`.

### 4. DNS records and transport
- A: IPv4 address for the website.
- AAAA: IPv6 address.
- CNAME: alias when a name points to another canonical name.
- MX: mail exchangers.
- NS: authoritative name servers.
- TXT: verification, SPF and other text policies.
DNS commonly uses UDP for efficient small queries. TCP is used for zone transfers and when responses are too large or truncated; modern DNS can also use encrypted transports such as DoT/DoH.

A very long TTL can leave old IP addresses cached after a move, causing users to reach the old server until caches expire.

### 5. Completed DNS code
See `Task04/dns_simulation.py`. It follows the longest matching suffix referral in the supplied server map and caches final IP answers. The third lookup returns zero queries because the first answer is cached. A production cache should store expiry timestamps and discard expired entries; this teaching program demonstrates cache hits without a time-based expiry.

### 6. CDN / anycast alternative
With a CDN/anycast DNS, the university's own authoritative infrastructure may receive fewer end-user lookups if the CDN hosts the delegated DNS zone or answers through its authoritative service. If the university remains authoritative for the original zone, queries for that zone can still reach its authoritative servers. Students in distant cities may receive an address for a nearby CDN edge, reducing content latency. Exact query counts depend on delegation and resolver cache behaviour.

**Recommendation:** Use a suitably long but operationally safe TTL for stable records, lower it before planned migrations, and use redundant authoritative DNS. For result day, CDN/anycast can improve content delivery and resilience.

---

## Q5 – When Will the Video Call Freeze?

M/M/1 model: service rate μ = 1,000 packets/s. Utilisation ρ = λ/μ, average number L = ρ/(1−ρ), average system delay W = 1/(μ−λ).

| Arrival λ (pkt/s) | Utilisation ρ | Average packets L | Average delay W |
|---:|---:|---:|---:|
| 500 | 0.50 | 1 | 2 ms |
| 800 | 0.80 | 4 | 5 ms |
| 900 | 0.90 | 9 | 10 ms |
| 950 | 0.95 | 19 | 20 ms |
| 990 | 0.99 | 99 | 100 ms |
| 1000 | 1.00 | Unstable | Unbounded |

The delay first exceeds 20 ms when λ is greater than 950 packets/s (at 950 it is exactly 20 ms). Increasing load from 450 to 900 packets/s changes delay from 1/(1000−450)=1.818 ms to 10 ms, a factor of 5.5, not ten. If comparing 500 to 900, delay rises from 2 ms to 10 ms, exactly 5 times. The queueing delay grows non-linearly as utilisation approaches 100%.

### Token bucket burst
Bucket size = 1 MB = 8 Mbit. Backup sends at 10 Mbps while allowed rate is 2 Mbps, so tokens are consumed at the excess rate 8 Mbps. Burst duration = 8 Mbit / 8 Mbps = **1 second** (assuming full bucket at start and decimal MB).

### DiffServ
- EF: low-latency voice/video packets (with admission control and policing).
- AF: important business traffic that can tolerate some queueing but deserves differentiated treatment.
- Best effort: ordinary browsing and non-urgent backup; shape/police backup to protect real-time traffic.

### Faster link vs QoS
QoS can protect delay-sensitive video by prioritising it and shaping backups, but cannot create capacity. A faster link is appropriate when sustained total demand exceeds capacity. Use both when needed.

### Capacity for less than 10 ms at 1,500 pkt/s
Require `1/(μ−1500) < 0.010`; therefore `μ−1500 > 100`, so **μ > 1,600 packets/s**. A practical link should be above 1,600 pkt/s with headroom.

### Alternative: 2,000 pkt/s link
At λ=1,800 and μ=2,000, W = 1/(2000−1800) = 0.005 s = **5 ms**. On the original 1,000 pkt/s link, total load 1,800 exceeds capacity and the queue is unstable. Strict priority for video can protect video delay, but backup traffic may be starved and overall overload remains; shaping backup and/or increasing capacity is safer.

**Result:** Queue utilisation, packet count, delay and token-bucket burst duration were calculated.

---

## Q6 – Count the Round Trips Before the First Byte

RTT = 100 ms. Simplified full-handshake assumptions:
- TCP + TLS 1.2: 1 RTT TCP handshake + 2 RTT TLS 1.2 full handshake = **3 RTT = 300 ms** before application request data.
- TCP + TLS 1.3: 1 RTT TCP handshake + 1 RTT TLS 1.3 handshake = **2 RTT = 200 ms**.
- QUIC first visit: transport and TLS 1.3 handshake are combined, typically **1 RTT = 100 ms** before normal application data.
- QUIC 0-RTT resumption: eligible early data can be sent immediately, **0 RTT additional wait** for sending the request; the server's response still depends on network and handshake processing.

Exact timing depends on TLS resumption, certificate mode, address validation, packet loss and implementation.

### 0-RTT replay risk
An attacker may capture and replay early data because the server has not yet completed the fresh handshake confirmation. Do not send non-idempotent operations such as money transfers, payments, account changes or one-time actions as 0-RTT. Use 0-RTT only for replay-safe requests, and validate authorization and anti-replay protections.

### Connection migration
QUIC uses a connection ID, so a connection can survive a change from Wi-Fi to 5G when the client IP/port changes, subject to path validation. Traditional TCP connections are identified by endpoint IP/port pairs; a path change normally breaks the connection and requires a new TCP/TLS connection.

### Firewall blocking
Some firewalls block or restrict UDP traffic used by QUIC. The app/browser should fall back to HTTPS over TCP with TLS (typically HTTP/2 or HTTP/1.1).

### 30-second transfer path change
At 100 ms RTT, TCP+TLS may need to establish a new TCP connection and TLS session after path change, costing approximately 2 RTT for a resumed TLS 1.3 connection or 3 RTT for a full TLS 1.2 handshake, plus retransmission/application recovery. QUIC can migrate the existing connection after path validation, often avoiding a full connection restart. Actual interruption depends on path validation and packet loss.

**Recommendation:** QUIC is attractive for a mobile banking app because it reduces setup latency and supports migration, but use TLS 1.3 security, avoid unsafe 0-RTT operations and provide TCP fallback.

---

## Q7 – Choose the Protocols from First Principles

### Stage 1 – Traffic requirements

| Traffic | Delay need | Loss/order need | Security |
|---|---|---|---|
| Live video consultation | Very low delay; target conversational latency measured end-to-end | Some loss can be concealed; late packets are less useful | Encrypt media and authenticate participants |
| Patient records and X-ray images | Delay tolerant compared with video | Complete, reliable, ordered delivery required | Strong confidentiality, integrity, access control and audit |
| Chat | Low/moderate delay | Reliable ordered messages | End-to-end or transport encryption and authentication |
| Hospital service-name lookup | Fast lookup | Correct DNS response | DNSSEC validation where available; encrypted client-to-resolver DNS if required |

Measurable design targets should be tested: video one-way latency/jitter and packet loss; file-transfer completion and hash integrity; chat delivery/order; DNS lookup latency and cache hit rate. The assignment does not prescribe numeric service-level thresholds, so the project team should set them with clinical users.

### Stage 2 – Protocol comparison and selection
- Live video: UDP-based real-time media (e.g. RTP/SRTP with congestion control) to avoid waiting for retransmission of late frames. QUIC/HTTP/3 may be used for compatible real-time application services, but ordinary HTTP/3 is not itself a replacement for a media transport design.
- Patient records/X-rays: HTTPS over TCP with TLS 1.3 or HTTP/3 over QUIC. Use resumable/chunked transfer, integrity hashes and retry.
- Chat: WebSocket over TLS/TCP or a reliable QUIC stream. Reliable ordering is important.
- Service lookup: DNS with caching and suitable TTL; use redundant recursive resolvers.
- HTTP/2: multiplexes streams but shares TCP head-of-line blocking.
- HTTP/3: uses QUIC streams, reducing cross-stream transport head-of-line blocking.
- TLS 1.3: provides confidentiality, integrity and authentication for supported application transports.

### TCP throughput limit
Window = 64 KB = 65,536 bytes (using 1 KB=1024 bytes), RTT = 0.3 s.
Throughput limit ≈ window / RTT = 65,536 / 0.3 = 218,453 bytes/s.
In bits/s: 218,453 × 8 = **1.75 Mbps** approximately.
This is a simplified window-limited upper bound before protocol overhead and loss. It means a large X-ray transfer over a 300 ms RTT path can be limited to around 1.75 Mbps unless the receive/congestion window is increased or parallelism/transport tuning is used.

### DNS and QoS
Use redundant recursive DNS resolvers close to health centres, cache stable records, and choose TTLs that balance load and failover. Give real-time voice/video an appropriately policed EF/low-latency queue; give clinical records/chat suitable assured forwarding (AF) or reliable best-effort with capacity; keep bulk backups low priority and shape them. Avoid allowing EF traffic to consume unlimited bandwidth.

### Stage 3 – Implementation and verification
Starter socket examples are in `Task07/`. Test file transfer with a SHA-256 digest and chat with ordered messages. Emulate 100–300 ms delay and up to 5% loss using `tc netem` on Linux or a network emulator. Record transfer completion time, missing/corrupt files, chat message order and latency. Actual measured results must be added after running the tests.

### Stage 4 – Defence and 5G
The design separates real-time media from reliable data transfer and protects patient information with encryption and authentication. With improved 5G latency/capacity, video quality and file transfer may improve, but coverage variation, congestion, handover and security still need testing. 5G does not remove the need for congestion control, QoS, encryption or fallback.

### Commercial vendor alternative
Ask the vendor for measured one-way latency, jitter and packet loss under weak 4G; adaptation and recovery behaviour; supported codecs and bandwidth; encryption in transit/at rest; key management; access controls; audit logs; data residency; retention/deletion; incident response; interoperability; uptime SLA; and independent security/privacy certifications. Choose it only after a pilot under representative 4G conditions, review of privacy/security documentation, and contractual guarantees for patient data.

**Final result:** Use low-latency UDP media, reliable encrypted streams for records/chat, resilient cached DNS and QoS that protects real-time traffic while shaping bulk transfers.
