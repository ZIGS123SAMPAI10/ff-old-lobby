from flask import Flask, request, Response
import sys
import os

# Import Protobuf asli Garena yang kamu punya
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)

# URL Vercel kamu (Pastikan ini yang kamu pasang di APK)
MY_URL = "https://private89veffold1lb123.vercel.app"

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"] )
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    # 1. HANDLING VER.PHP (Protokol Asli Garena 2018)
    if "ver.php" in path:
        # Garena asli pake format ini buat bilang 'Gak ada Update'
        res_text = "version=1.26.3\nupdate=0\nforce_update=0\ndownload_url=\nmsg="
        return Response(res_text, mimetype="text/plain")

    # 2. HANDLING LOGIN (Protokol Protobuf Asli Garena)
    # Setelah ver.php sukses, game bakal POST data login ke server
    if request.method == "POST":
        try:
            # Kita buat jawaban Protobuf yang 100% cocok sama MajorLogin.proto
            res = MajorLogin_pb2.response()
            res.accountId = 1000001
            res.token = "GUEST_LOGIN_SUCCESS_2018"
            res.serverUrl = MY_URL # Game harus tau dia konek ke mana selanjutnya
            res.ipRegion = "ID"
            res.notiRegion = "ID"
            res.lockRegion = "ID"
            res.ttl = 86400 # Token berlaku 24 jam
            
            # Garena asli biasanya minta region rekomendasi
            res.recommendRegions.append("ID")
            
            return Response(
                res.SerializeToString(),
                mimetype="application/x-protobuf",
                headers={"Content-Type": "application/x-protobuf"}
            )
        except Exception as e:
            # Kalau ada error, kita tetep jawab biar gak plonga-plongo
            return "OK", 200

    # 3. HANDLING LAINNYA (Notice, dll)
    return ""

# Objek app untuk Vercel
app = app
