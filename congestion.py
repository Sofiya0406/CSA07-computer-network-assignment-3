"""Simplified TCP congestion-window model from the assignment."""
def simulate(losses, ssthresh=16, reno=True):
    cwnd, trace = 1, []
    for rtt in range(1, 21):
        trace.append(cwnd)
        if rtt in losses:
            ssthresh = max(cwnd // 2, 2)
            cwnd = ssthresh if reno else 1
        elif cwnd < ssthresh:
            cwnd = min(cwnd * 2, ssthresh)
        else:
            cwnd += 1
    return trace

for label, reno in (("Reno ", True), ("Tahoe", False)):
    tr = simulate({8, 14}, reno=reno)
    print(label, " ".join(f"{w:2d}" for w in tr), f"| segments sent {sum(tr)}")
