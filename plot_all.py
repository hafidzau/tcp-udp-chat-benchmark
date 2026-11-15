# Jalankan dari folder srcjarkom: py plot_all.py
# Butuh: Normal/rtt_tcp.csv, Normal/rtt_udp.csv, loss/rtt_tcp_loss.csv, loss/rtt_udp_loss.csv
# Output: grafik_rtt_normal.png, grafik_rtt_loss.png, grafik_rtt_avg.png,
#         grafik_ack_rate.png, ringkasan_rtt.csv
import csv, statistics
import matplotlib.pyplot as plt

FILES = {
    ("TCP", "Normal"):   "Normal/rtt_tcp.csv",
    ("UDP", "Normal"):   "Normal/rtt_udp.csv",
    ("TCP", "Loss 10%"): "loss/rtt_tcp_loss.csv",
    ("UDP", "Loss 10%"): "loss/rtt_udp_loss.csv",
}
COLOR = {"TCP": "#2563eb", "UDP": "#f59e0b"}

def load(fn):
    ys, lost = [], 0
    with open(fn) as f:
        for r in csv.DictReader(f):
            if r["rtt_ms"]:
                ys.append(float(r["rtt_ms"]))
            else:
                ys.append(float("nan")); lost += 1
    return ys, lost

data, stats = {}, []
for (proto, scen), fn in FILES.items():
    ys, lost = load(fn)
    ok = [y for y in ys if y == y]
    data[(proto, scen)] = ys
    stats.append({
        "protokol": proto, "skenario": scen, "total_pesan": len(ys),
        "di_ack": len(ok), "tanpa_ack": lost,
        "ack_rate_%": round(len(ok) / len(ys) * 100, 1),
        "rtt_avg_ms": round(statistics.mean(ok), 3),
        "rtt_median_ms": round(statistics.median(ok), 3),
        "rtt_min_ms": round(min(ok), 3), "rtt_max_ms": round(max(ok), 3),
        "rtt_stdev_ms": round(statistics.pstdev(ok), 3),
    })

with open("ringkasan_rtt.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=stats[0].keys())
    w.writeheader(); w.writerows(stats)
for s in stats:
    print(s)

def line_chart(scen, fn, log=False):
    plt.figure(figsize=(8, 4))
    for proto in ("TCP", "UDP"):
        ys = data[(proto, scen)]
        plt.plot(range(len(ys)), ys, label=proto, color=COLOR[proto], marker="o", markersize=2.5, linewidth=1)
    if log: plt.yscale("log")
    plt.xlabel("Nomor pesan"); plt.ylabel("RTT (ms)" + (" - skala log" if log else ""))
    plt.title(f"RTT per pesan, TCP vs UDP ({scen})")
    plt.legend(); plt.grid(True, alpha=.3); plt.tight_layout()
    plt.savefig(fn, dpi=200); plt.close()

line_chart("Normal", "grafik_rtt_normal.png")
line_chart("Loss 10%", "grafik_rtt_loss.png", log=True)

def bar_chart(key, ylabel, title, fn, log=False, fmt="{:.2f}"):
    scens = ["Normal", "Loss 10%"]
    plt.figure(figsize=(6, 4))
    w = 0.35
    for i, proto in enumerate(("TCP", "UDP")):
        vals = [next(s[key] for s in stats if s["protokol"] == proto and s["skenario"] == sc) for sc in scens]
        xs = [j + (i - 0.5) * w for j in range(len(scens))]
        bars = plt.bar(xs, vals, w, label=proto, color=COLOR[proto])
        for b, v in zip(bars, vals):
            plt.text(b.get_x() + b.get_width() / 2, v, fmt.format(v), ha="center", va="bottom", fontsize=8)
    plt.xticks(range(len(scens)), scens)
    if log: plt.yscale("log")
    plt.ylabel(ylabel); plt.title(title); plt.legend(); plt.grid(True, axis="y", alpha=.3)
    plt.tight_layout(); plt.savefig(fn, dpi=200); plt.close()

bar_chart("rtt_avg_ms", "RTT rata-rata (ms) - skala log", "RTT rata-rata TCP vs UDP", "grafik_rtt_avg.png", log=True, fmt="{:.3f}")
bar_chart("ack_rate_%", "Pesan di-ACK (%)", "Keandalan pesan (di-ACK server)", "grafik_ack_rate.png", fmt="{:.0f}%")
print("Selesai: 4 grafik + ringkasan_rtt.csv")
