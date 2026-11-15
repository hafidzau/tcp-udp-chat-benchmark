import csv

HOST = "127.0.0.1"
TCP_PORT, UDP_PORT = 5000, 5001
SIZE = 100   # setiap pesan chat = 100 byte (frame tetap)
N = 100      # jumlah pesan pengujian

def pack(text):
    return text.encode()[:SIZE].ljust(SIZE, b" ")

def unpack(b):
    return b.decode(errors="replace").rstrip()

def chat_msg(seq, user, text):
    return pack(f"{seq:04d}|{user}|{text}")

def ack_msg(seq):
    return pack(f"ACK|{seq:04d}")

def is_ack(txt):
    return txt.startswith("ACK|")

def show(txt):
    p = txt.split("|", 2)
    return f"[{p[1]}] {p[2]}" if len(p) == 3 else txt

def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("closed")
        buf += chunk
    return buf

def save_csv(fn, rows):
    with open(fn, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["seq", "rtt_ms"])
        w.writerows(rows)

def report(proto, rtts, ok, lost, total):
    print(f"[{proto}] pesan di-ACK server : {ok}/{N}, tanpa ACK: {lost} ({lost/N*100:.1f}%)")
    if rtts:
        print(f"[{proto}] RTT avg/min/max     : {sum(rtts)/len(rtts):.3f} / {min(rtts):.3f} / {max(rtts):.3f} ms")
    print(f"[{proto}] throughput payload  : {ok*SIZE/total/1024:.2f} KB/s, total waktu {total:.3f}s")

def report_received(received):
    if not received:
        print("Pesan diterima: 0")
        return
    missing = sorted(set(range(min(received), max(received) + 1)) - received)
    print(f"Pesan diterima: {len(received)}, hilang: {len(missing)} {missing[:20]}")
