rtt_ms = 100
cases = {
    "TCP + TLS 1.2 full handshake": 3,
    "TCP + TLS 1.3 full handshake": 2,
    "QUIC first visit": 1,
    "QUIC 0-RTT early request": 0,
}
for name, rtts in cases.items():
    print(f"{name}: {rtts} RTT = {rtts * rtt_ms} ms")
