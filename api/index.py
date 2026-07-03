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

# URL Vercel kamu
MY_URL = "https://private89veffold1lb123.vercel.app"

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"] )
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    # Log setiap request yang masuk (Penting!)
    print(f"[*] Request: {request.method} /{path}")

    # 1. HANDLING LOGIN (POST Request)
    # Ini adalah tahap setelah ver.php sukses
    if request.method == "POST":
        print(f"[*] Mendeteksi POST payload sebesar {len(request.get_data())} bytes")
        try:
            # Kita buat respon Protobuf yang bikin game 'senang'
            res = MajorLogin_pb2.response()
            res.accountId = 12345678  # ID Akun Dummy
            res.token = "GUEST_SUCCESS_PROJECT_REVENGER"
            res.serverUrl = MY_URL    # Arahkan game tetap ke server kita
            res.ipRegion = "ID"
            res.notiRegion = "ID"
            res.lockRegion = "ID"
            res.ttl = 86400           # Token berlaku 24 jam
            
            # Tambahkan rekomendasi region agar data lebih lengkap
            res.recommendRegions.append("ID")
            
            # Kirim balik dalam format Binary Protobuf
            return Response(
                res.SerializeToString(),
                mimetype="application/x-protobuf",
                headers={
                    "Content-Type": "application/x-protobuf",
                    "Server": "Garena"
                }
            )
        except Exception as e:
            print(f"[!] Gagal membuat respon Protobuf: {e}")
            return "OK", 200

    # 2. HANDLING VER.PHP (Tetap kita jaga)
    if "ver.php" in path:
        return "1.26.3"

    return "Server Project Revenger: Pintu Login Terbuka! 🗿", 200

# Vercel butuh objek 'app'
app = app
