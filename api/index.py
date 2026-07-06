from flask import Flask, request, Response
import sys
import os
import socket

app = Flask(__name__)

# ====================================================================
# JALUR JEMBATAN KE TERMUX KAMU
# ====================================================================
PAGEKITE_DOMAIN = "ffkipasold.pagekite.me"
PAGEKITE_PORT   = 14000
# ====================================================================

def forward_to_termux(data_mentah):
    """Meneruskan paket data login biner langsung ke TCP Termux"""
    try:
        ip_angka = socket.gethostbyname(PAGEKITE_DOMAIN)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)
        s.connect((ip_angka, PAGEKITE_PORT))
        s.sendall(data_mentah)
        respons_dari_termux = s.recv(4096)
        s.close()
        return respons_dari_termux
    except Exception as e:
        print(f"[-] Gagal oper data ke Termux: {e}")
        return None

# Menangkap semua jenis url, baik di folder root, /live/, atau sub-folder lainnya
@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    
    # 1. BYPASS AMAN UNTUK PENCEGAHAN DOWNLOAD GAGAL
    # Jika game meminta file ver.php, notice, atau file update di folder live
    if "ver.php" in path or "live" in path or "notice" in path:
        # Kirimkan teks versi polosan yang diminta game
        return Response("1.26.3", mimetype="text/plain", status=200)

    # 2. PROSES OPER DATA LOGIN KE TERMUX
    if request.method == "POST":
        data_paket_game = request.get_data()
        if data_paket_game:
            print("[*] Vercel menerima paket login, meneruskan ke Termux...")
            balasan_protobuf = forward_to_termux(data_paket_game)
            
            if balasan_protobuf:
                return Response(
                    balasan_protobuf,
                    mimetype="application/x-protobuf",
                    headers={
                        "Content-Type": "application/x-protobuf",
                        "Server": "Garena-Gatekeeper"
                    }
                )
        return "Gagal menyambung ke backend Termux", 502

    return "Gerbang Utama FF Old Vercel Aktif! 🗿", 200

app = app
