import socket
from common import *

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, UDP_PORT))
clients = set()
print(f"[UDP] Chat server di {HOST}:{UDP_PORT}")
while True:
    try:
        data, addr = s.recvfrom(2048)
    except ConnectionResetError:
        continue
    txt = unpack(data)
    if addr not in clients:
        clients.add(addr); print("JOIN :", addr)
    if txt.startswith("JOIN"):
        continue
    try:
        seq = int(txt[:4])
    except ValueError:
        continue
    for c in clients:
        if c != addr:
            try: s.sendto(data, c)          # relay ke client lain
            except OSError: pass
    try: s.sendto(ack_msg(seq), addr)       # ACK ke pengirim
    except OSError: pass
