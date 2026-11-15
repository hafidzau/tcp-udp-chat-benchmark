# Chat TCP vs UDP (Python 3, tanpa library tambahan)

Workload: 100 pesan x 100 byte (format `seq|user|isi`, dipadatkan 100 byte).
Topologi: localhost 127.0.0.1. Port TCP 5000, UDP 5001.

## Menjalankan (3 terminal per protokol, jalankan berurutan)
TCP:
  1. python tcp_server.py
  2. python tcp_client.py chat rx      (penerima)
  3. python tcp_client.py auto bot     (pengirim, 100 pesan)
UDP:
  1. python udp_server.py
  2. python udp_client.py chat rx
  3. python udp_client.py auto bot

Setelah bot selesai, tekan Ctrl+C di terminal penerima untuk melihat
jumlah pesan yang diterima/hilang. Demo manual: jalankan 2 client `chat` dan ketik pesan.

Output: rtt_tcp.csv, rtt_udp.csv. Grafik: pip install matplotlib && python plot.py
Wireshark: interface loopback, filter `tcp.port == 5000` / `udp.port == 5001`.
Mode 2 laptop: ganti HOST di common.py dengan IP server, dan bind server ke 0.0.0.0.
