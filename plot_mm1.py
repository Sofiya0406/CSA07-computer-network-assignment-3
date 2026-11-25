"""Optional: plot M/M/1 delay versus arrival rate (requires matplotlib)."""
import matplotlib.pyplot as plt
mu = 1000
loads = list(range(100, 1000, 10))
delays_ms = [1000 / (mu - lam) for lam in loads]
plt.plot(loads, delays_ms)
plt.xlabel("Arrival rate (packets/second)")
plt.ylabel("Average system delay (ms)")
plt.title("M/M/1 Queue Delay")
plt.grid(True)
plt.show()
