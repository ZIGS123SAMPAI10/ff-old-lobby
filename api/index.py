from flask import Flask, request, Response
import sys
import os

# Setup path agar bisa baca MajorLogin_pb2
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)

# ALAMAT SERVER LOBBY (TCP) KAMU
# Ini adalah link yang akan dituju game setelah melewati Gerbang Vercel
LOBBY_TCP = "g1dw3aegfh.localto.net:7943"

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
            # Kita buat respon Protobuf (Tiket Login)
            res = MajorLogin_pb2.response()
            res.accountId = 1000001
            res.token = "GUEST_LOGIN_SUCCESS"
            
            # KUNCI UTAMA: Di sini kita arahkan game ke link localto.net kamu
            # Begitu dapet data ini, game bakal mutusin koneksi HTTPS Vercel 
            # dan langsung buka koneksi TCP ke g1dw3aegfh.localto.net:5034
            res.serverUrl = LOBBY_TCP
            
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
