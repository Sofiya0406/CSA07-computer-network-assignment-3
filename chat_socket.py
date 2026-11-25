"""Minimal ordered TCP chat-message demonstration on loopback."""
import socket, threading

HOST, PORT = "127.0.0.1", 50071
messages = [b"Hello doctor\n", b"Patient record is ready\n", b"Thank you\n"]

def server():
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        conn, _ = s.accept()
        with conn:
            stream = b""
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                stream += chunk
            for line in stream.decode().splitlines():
                print("Received:", line)

t = threading.Thread(target=server)
t.start()
with socket.create_connection((HOST, PORT)) as c:
    for msg in messages:
        c.sendall(msg)
t.join()
