from flask import Flask, request, Response
import sys
import os
import socket

# Setup path agar bisa baca MajorLogin_pb2
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)

# ====================================================================
# KONFIGURASI SERVER TERMUX KAMU (PAGEKITE)
# ====================================================================
PAGEKITE_DOMAIN = "ffkipasold.pagekite.me"
PAGEKITE_PORT   = 14000
# ====================================================================

def get_lobby_tcp_address():
    """Fungsi otomatis mengubah domain Pagekite menjadi IP angka:port"""
    try:
        # Mengubah 'ffkipasold.pagekite.me' menjadi IP angka (contoh: 139.162.5.63)
        ip_angka = socket.gethostbyname(PAGEKITE_DOMAIN)
        print(f"[SUCCESS] Resolving IP: {ip_angka}:{PAGEKITE_PORT}")
        return f"{ip_angka}:{PAGEKITE_PORT}"
    except socket.gaierror:
        # Jika gagal/Pagekite mati, pakai fallback IP relay cadangan agar script tidak crash
        print("[WARNING] Gagal resolve domain Pagekite, menggunakan IP fallback.")
        return f"139.162.5.63:{PAGEKITE_PORT}"

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    # 1. GERBANG UTAMA: ver.php
    # Tugasnya: Mastiin game gak 'Download Gagal'
    if "ver.php" in path:
        # Kita pake respon paling simpel yang tadi sempat berhasil lolos
        return Response("1.26.3", mimetype="text/plain")

    # 2. PROSES PENGARAHAN (Login Phase)
    # Setelah ver.php sukses, game akan melakukan POST untuk minta data login
    if request.method == "POST":
        try:
            # Ambil alamat IP Angka + Port dari Pagekite secara real-time
            lobby_address_resolved = get_lobby_tcp_address()

            # Kita buat respon Protobuf (Tiket Login)
            res = MajorLogin_pb2.response()
            res.accountId = 1000001
            res.token = "GUEST_LOGIN_SUCCESS"
            
            # KUNCI UTAMA: Mengirimkan IP Angka hasil konversi ke APK game
            # Game akan langsung membuka koneksi TCP ke IP tersebut (Port 14000)
            res.serverUrl = lobby_address_resolved
            
            res.ipRegion = "ID"
            res.notiRegion = "ID"
            res.lockRegion = "ID"
            res.ttl = 86400
            res.recommendRegions.append("ID")
            
            return Response(
                res.SerializeToString(),
                mimetype="application/x-protobuf",
                headers={
                    "Content-Type": "application/x-protobuf",
                    "Server": "Garena-Gatekeeper"
                }
            )
        except Exception as e:
            print(f"Error: {e}")
            return "OK", 200

    return "Gerbang Utama FF Old Vercel Aktif! 🗿", 200

# Objek app untuk Vercel
app = app
            
