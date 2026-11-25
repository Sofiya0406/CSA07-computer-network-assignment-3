"""Iterative DNS resolution through root, TLD and authoritative servers."""
import ipaddress

SERVERS = {
    "root": {"in.": "tld-in", "com.": "tld-com"},
    "tld-in": {"ac.in.": "ns-ac"},
    "tld-com": {"example.com.": "ns-example"},
    "ns-ac": {"simats.ac.in.": "ns-simats"},
    "ns-simats": {"results.simats.ac.in.": "10.20.30.40"},
    "ns-example": {"www.example.com.": "93.184.216.34"},
}
cache = {}

def resolve(name):
    if name in cache:
        return cache[name], 0
    server, queries = "root", 0
    while True:
        queries += 1
        matches = [(suffix, target) for suffix, target in SERVERS[server].items()
                   if name.endswith(suffix)]
        if not matches:
            raise LookupError(f"No referral/answer for {name} at {server}")
        suffix, target = max(matches, key=lambda item: len(item[0]))
        try:
            ipaddress.ip_address(target)
            cache[name] = target
            return target, queries
        except ValueError:
            server = target

for n in ("results.simats.ac.in.", "www.example.com.", "results.simats.ac.in."):
    ip, q = resolve(n)
    print(f"{n:<24} {ip:<15} queries sent: {q}")
