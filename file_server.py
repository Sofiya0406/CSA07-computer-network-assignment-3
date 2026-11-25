"""Small TCP file-transfer example with SHA-256 integrity check."""
import hashlib
import socket
import threading

HOST, PORT = "127.0.0.1", 50070
DATA = b"Sample patient-record transfer. Replace with a permitted test file."

def server():
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)
        conn, _ = s.accept()
        with conn:
            received = bytearray()
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                received.extend(chunk)
            print("Server received bytes:", len(received))
            print("Server SHA256:", hashlib.sha256(received).hexdigest())

thread = threading.Thread(target=server)
thread.start()
with socket.create_connection((HOST, PORT)) as client:
    client.sendall(DATA)
thread.join()
print("Client SHA256:", hashlib.sha256(DATA).hexdigest())
