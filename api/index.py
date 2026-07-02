from flask import Flask, request, Response
import sys
import os

# Import Protobuf
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)

# URL Vercel kamu (Tanpa spasi, pastikan benar)
MY_URL = "https://private89veffold1lb123.vercel.app"

@app.route("/", defaults={"path": ""} )
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    print(f"[*] Request Masuk: {path}")

    # 1. HANDLING VER.PHP DENGAN PROTOBUF LENGKAP
    if "ver.php" in path:
        res = MajorLogin_pb2.response()
        res.accountId = 0 # 0 biasanya untuk pengecekan awal
        res.token = "GUEST_TOKEN_REV"
        res.serverUrl = MY_URL
        res.ipRegion = "ID"
        res.notiRegion = "ID"
        res.lockRegion = "ID"
        res.ttl = 86400 # Kita kasih waktu 24 jam biar gak timeout/loading lama
        
        # Tambahkan region rekomendasi (biar RX datanya lebih besar mirip screenshot kamu)
        res.recommendRegions.append("ID")
        res.recommendRegions.append("US")
        
        return Response(
            res.SerializeToString(),
            mimetype="application/x-protobuf"
        )

    # 2. HANDLING LOGIN (POST)
    if request.method == "POST":
        res = MajorLogin_pb2.response()
        res.accountId = 12345678
        res.token = "LOGIN_SUCCESS_PROJECT_REVENGER"
        res.serverUrl = MY_URL
        return Response(res.SerializeToString(), mimetype="application/x-protobuf")

    return "Server Project Revenger 1.26.3 Online! 🗿"

if __name__ == "__main__":
    app.run()
    
