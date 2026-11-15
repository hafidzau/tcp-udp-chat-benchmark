import socket, threading
from common import *

clients, lock = [], threading.Lock()

def handle(conn, addr):
    with lock:
        clients.append(conn)
    print("JOIN :", addr)
    try:
        while True:
            data = recv_exact(conn, SIZE)
            seq = int(unpack(data)[:4])
            with lock:
                for c in clients:
                    if c is not conn:
                        try: c.sendall(data)      # relay ke client lain
                        except OSError: pass
                conn.sendall(ack_msg(seq))        # ACK ke pengirim
    except (ConnectionError, OSError, ValueError):
        pass
    finally:
        with lock:
            if conn in clients: clients.remove(conn)
        conn.close()
        print("LEAVE:", addr)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, TCP_PORT))
s.listen()
print(f"[TCP] Chat server di {HOST}:{TCP_PORT}")
while True:
    conn, addr = s.accept()
    threading.Thread(target=handle, args=(conn, addr), daemon=True).start()
