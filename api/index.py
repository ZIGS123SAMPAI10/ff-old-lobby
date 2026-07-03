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

# URL Vercel tanpa 'https://' dan dipaksa tembak port HTTPS (443)
# Ini format krusial biar APK gak parsing eror dan balik ke IP Garena asli
MY_GAME_SERVER = "private89veffold1lb123.vercel.app:443"

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    path_lower = path.lower()

    # 1. HANDLING VER.PHP (Pengecekan Versi / Update Game)
    if "ver.php" in path_lower or "version" in path_lower:
        res_text = "version=1.26.3\nupdate=0\nforce_update=0\ndownload_url=\nmsg="
        return Response(res_text, mimetype="text/plain")

    # 2. HANDLING LOGIN PROTOBUF
    # Kita filter biar bener-bener merespon pas APK minta endpoint login (misal /login, /login_server, dll)
    if request.method == "POST" and ("login" in path_lower or "auth" in path_lower):
        try:
            # Buat instance response sesuai file proto lu
            res = MajorLogin_pb2.response()
            res.accountId = 1000001
            res.token = "GUEST_LOGIN_SUCCESS_2018"
            
            # PAKSA GAME UNTUK TETEP DI VERCEL VIA PORT 443
            res.serverUrl = MY_GAME_SERVER 
            
            res.ipRegion = "ID"
            res.notiRegion = "ID"
            res.lockRegion = "ID"
            res.ttl = 86400  # Token aktif 24 jam
            res.recommendRegions.append("ID")
            
            return Response(
                res.SerializeToString(),
                mimetype="application/x-protobuf",
                headers={
                    "Content-Type": "application/x-protobuf",
                    "Cache-Control": "no-cache"
                }
            )
        except Exception as e:
            # Jika ada error internal protobuf, balikkan status 500 biar gampang di-debug di log Vercel
            return f"Error Protobuf: {str(e)}", 500

    # 3. HANDLING MAINTENANCE / NOTICE / CONFIG LAINNYA
    # Kalau game nyari file json, txt, atau konfigurasi lain, kasih respon kosong/OK 
    # biar game gak mandek (stuck) plonga-plongo nungguin server.
    if request.method == "POST":
        return "OK", 200
        
    return ""

# Objek app untuk dibaca oleh serverless Vercel
app = app
