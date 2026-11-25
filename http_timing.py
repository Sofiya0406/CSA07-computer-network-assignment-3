from math import ceil
rtt_ms = 50
objects = 80
print("Non-persistent sequential:", (objects + 1) * 2 * rtt_ms, "ms")
print("Persistent no pipelining:", (2 + objects) * rtt_ms, "ms")
print("Persistent pipelining:", 3 * rtt_ms, "ms")
print("6 parallel non-persistent:", (2 + 2 * ceil(objects / 6)) * rtt_ms, "ms")
bundles = 8
print("8 bundles, non-persistent:", (bundles + 1) * 2 * rtt_ms, "ms")
print("8 bundles, persistent:", (2 + bundles) * rtt_ms, "ms")
