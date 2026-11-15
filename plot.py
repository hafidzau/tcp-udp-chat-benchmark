import csv
import os

import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "grafik")
os.makedirs(OUT, exist_ok=True)

# Sumber data (relatif terhadap folder plot.py)
FILES = {
    "TCP normal": "Normal/rtt_tcp.csv",
    "UDP normal": "Normal/rtt_udp.csv",
    "TCP loss": "loss/rtt_tcp_loss.csv",
    "UDP loss": "loss/rtt_udp_loss.csv",
}

# Isi dari output terminal 'auto bot' (satuan KB/s). Biarkan None jika belum ada.
THROUGHPUT = {
    "TCP normal": 360.94,
    "UDP normal": 332.64,
    "TCP loss": 1.50,   # turunan: 100 pesan x 100 B / total RTT (~6,52 s)
    "UDP loss": 0.29,
}

COLOR = {"TCP": "#2563eb", "UDP": "#f59e0b"}


def load(path):
    """Kembalikan (seq, rtt) dengan rtt = None untuk pesan tanpa ACK."""
    seq, rtt = [], []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            seq.append(int(r["seq"]))
            rtt.append(float(r["rtt_ms"]) if r["rtt_ms"] else None)
    return seq, rtt


data = {}
for name, rel in FILES.items():
    p = os.path.join(BASE, rel)
    if os.path.exists(p):
        data[name] = load(p)
    else:
        print(f"[lewati] {name}: file tidak ditemukan -> {p}")


def valid(name):
    return [v for v in data[name][1] if v is not None]


def rtt_line(names, title, fname, logy=False):
    """Grafik RTT per pesan. Pesan tanpa ACK ditandai X di dasar grafik, garis diputus."""
    names = [n for n in names if n in data]
    if len(names) < 2:
        return
    plt.figure(figsize=(8, 4))
    ymax = max(max(valid(n)) for n in names)
    ymin = min(min(valid(n)) for n in names)
    marker_y = ymin * 0.6 if logy else 0
    for n in names:
        seq, rtt = data[n]
        proto = n.split()[0]
        y = [v if v is not None else float("nan") for v in rtt]
        plt.plot(seq, y, label=n, color=COLOR[proto])
        lost = [s for s, v in zip(seq, rtt) if v is None]
        if lost:
            plt.scatter(lost, [marker_y] * len(lost), marker="x", color="red",
                        label=f"{n}: tanpa ACK ({len(lost)})", zorder=3)
    if logy:
        plt.yscale("log")
        plt.ylim(bottom=ymin * 0.4, top=ymax * 2)
        plt.ylabel("RTT (ms) - skala log")
    else:
        plt.ylim(bottom=-0.06 * ymax)
        plt.ylabel("RTT (ms)")
    plt.xlabel("Nomor pesan")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, fname), dpi=200)
    plt.close()


rtt_line(["TCP normal", "UDP normal"], "RTT TCP vs UDP (kondisi normal)", "grafik_rtt_normal.png")
rtt_line(["TCP loss", "UDP loss"], "RTT TCP vs UDP (Drop 10%)", "grafik_rtt_loss.png", logy=True)

# Rata-rata RTT
names = list(data)
if names:
    plt.figure(figsize=(6, 4))
    avgs = [sum(valid(n)) / len(valid(n)) for n in names]
    plt.bar(names, avgs, color=[COLOR[n.split()[0]] for n in names])
    for i, a in enumerate(avgs):
        plt.text(i, a, f"{a:.3f}", ha="center", va="bottom", fontsize=8)
    plt.yscale("log")
    plt.ylabel("RTT rata-rata (ms) - skala log")
    plt.title("RTT rata-rata")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "grafik_rtt_avg.png"), dpi=200)
    plt.close()

# Throughput (hanya yang sudah diisi)
tp = {n: v for n, v in THROUGHPUT.items() if v is not None}
if tp:
    plt.figure(figsize=(6, 4))
    plt.bar(list(tp), list(tp.values()), color=[COLOR[n.split()[0]] for n in tp])
    for i, v in enumerate(tp.values()):
        plt.text(i, v, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
    plt.yscale("log")
    plt.ylabel("Throughput payload (KB/s) - skala log")
    plt.title("Throughput")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "grafik_throughput.png"), dpi=200)
    plt.close()

# Integritas: pesan ber-ACK vs tanpa ACK
if names:
    ok = [len(valid(n)) for n in names]
    lost = [len(data[n][1]) - len(valid(n)) for n in names]
    plt.figure(figsize=(6, 4))
    plt.bar(names, ok, label="Di-ACK", color="#16a34a")
    plt.bar(names, lost, bottom=ok, label="Tanpa ACK", color="#dc2626")
    for i, (o, l) in enumerate(zip(ok, lost)):
        if l:
            plt.text(i, o + l / 2, str(l), ha="center", va="center", color="white")
    plt.ylabel("Jumlah pesan")
    plt.title("Integritas data di sisi pengirim")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "grafik_integritas.png"), dpi=200)
    plt.close()

# Ringkasan angka untuk tabel Bab IV
print(f"{'Kondisi':<12}{'ACK':>6}{'Tanpa ACK':>11}{'avg':>9}{'min':>9}{'max':>9}")
for n in names:
    v = valid(n)
    print(f"{n:<12}{len(v):>6}{len(data[n][1]) - len(v):>11}"
          f"{sum(v) / len(v):>9.3f}{min(v):>9.3f}{max(v):>9.3f}")
print(f"\nGrafik tersimpan di: {OUT}")