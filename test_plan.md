# Q7 test plan

Run the socket examples locally first. For network impairment, use a Linux test machine or emulator and apply delay/loss only to a controlled test interface, for example:
```bash
sudo tc qdisc add dev eth0 root netem delay 200ms loss 5%
# Remove after testing:
sudo tc qdisc del dev eth0 root
```
Record:
- configured delay and loss
- file size, transfer duration and SHA-256 match
- chat message count/order and delivery time
- video latency, jitter, packet loss and subjective quality (for an actual media test)
- DNS lookup time and cache hit/miss
Do not run `tc` on an interface carrying important traffic.
