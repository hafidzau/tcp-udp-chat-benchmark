# Pakai: python udp_client.py auto <nama>   -> bot kirim 100 pesan (pengujian)
#        python udp_client.py chat <nama>   -> chat interaktif / penerima
import socket, threading, time, sys
from common import *

mode = sys.argv[1] if len(sys.argv) > 1 else "auto"
user = sys.argv[2] if len(sys.argv) > 2 else "user"
SERVER = (HOST, UDP_PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for _ in range(3):   # kirim JOIN 3x supaya tetap terdaftar walau ada paket hilang
    s.sendto(pack("JOIN|" + user), SERVER)   # UDP tanpa koneksi: daftar ke server
    time.sleep(0.05)

ack_ev, last_ack, received = threading.Event(), [-1], set()

def receiver():
    while True:
        try:
            data, _ = s.recvfrom(2048)
        except ConnectionResetError:
            continue
        except OSError:
            break
        txt = unpack(data)
        try:
            if is_ack(txt):
                last_ack[0] = int(txt[4:8]); ack_ev.set()
            else:
                received.add(int(txt[:4]))
                if mode == "chat": print("\n" + show(txt))
        except ValueError:
            pass

threading.Thread(target=receiver, daemon=True).start()

if mode == "auto":
    rtts, rows, ok = [], [], 0
    start = time.perf_counter()
    for i in range(N):
        ack_ev.clear()
        t0 = time.perf_counter()
        s.sendto(chat_msg(i, user, "A" * SIZE), SERVER)
        if ack_ev.wait(1) and last_ack[0] == i:
            r = (time.perf_counter() - t0) * 1000
            rtts.append(r); rows.append((i, r)); ok += 1
        else:
            rows.append((i, ""))
    total = time.perf_counter() - start
    s.close()
    save_csv("rtt_udp.csv", rows)
    report("UDP", rtts, ok, N - ok, total)
else:
    print(f"Terhubung sebagai {user}. Ketik pesan, /quit atau Ctrl+C untuk keluar.")
    seq = 0
    try:
        while True:
            text = input("> ")
            if text == "/quit": break
            s.sendto(chat_msg(seq, user, text), SERVER); seq += 1
    except (KeyboardInterrupt, EOFError):
        pass
    s.close()
    report_received(received)
