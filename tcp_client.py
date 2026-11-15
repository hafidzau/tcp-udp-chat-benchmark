# Pakai: python tcp_client.py auto <nama>   -> bot kirim 100 pesan (pengujian)
#        python tcp_client.py chat <nama>   -> chat interaktif / penerima
import socket, threading, time, sys
from common import *

mode = sys.argv[1] if len(sys.argv) > 1 else "auto"
user = sys.argv[2] if len(sys.argv) > 2 else "user"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
t = time.perf_counter()
s.connect((HOST, TCP_PORT))
conn_ms = (time.perf_counter() - t) * 1000

ack_ev, last_ack, received = threading.Event(), [-1], set()

def receiver():
    try:
        while True:
            txt = unpack(recv_exact(s, SIZE))
            if is_ack(txt):
                last_ack[0] = int(txt[4:8]); ack_ev.set()
            else:
                received.add(int(txt[:4]))
                if mode == "chat": print("\n" + show(txt))
    except (ConnectionError, OSError):
        pass

def close_conn():
    # tutup koneksi dengan rapi supaya terlihat FIN/ACK di Wireshark
    try:
        s.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    s.close()

threading.Thread(target=receiver, daemon=True).start()

if mode == "auto":
    rtts, rows, ok = [], [], 0
    start = time.perf_counter()
    for i in range(N):
        ack_ev.clear()
        t0 = time.perf_counter()
        s.sendall(chat_msg(i, user, "A" * SIZE))
        if ack_ev.wait(5) and last_ack[0] == i:
            r = (time.perf_counter() - t0) * 1000
            rtts.append(r); rows.append((i, r)); ok += 1
        else:
            rows.append((i, ""))
    total = time.perf_counter() - start
    close_conn()
    save_csv("rtt_tcp.csv", rows)
    print(f"[TCP] connect time: {conn_ms:.3f} ms")
    report("TCP", rtts, ok, N - ok, total)
else:
    print(f"Terhubung sebagai {user}. Ketik pesan, /quit atau Ctrl+C untuk keluar.")
    seq = 0
    try:
        while True:
            text = input("> ")
            if text == "/quit": break
            s.sendall(chat_msg(seq, user, text)); seq += 1
    except (KeyboardInterrupt, EOFError):
        pass
    close_conn()
    report_received(received)