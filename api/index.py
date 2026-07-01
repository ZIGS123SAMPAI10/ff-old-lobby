from flask import Flask, request, Response
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)

# Link Server Kamu
MY_URL = "https://private89veffold1lb123.vercel.app"

@app.route("/" )
@app.route("/<path:path>")
def catch_all(path):
    # Ambil versi dari game (1.26.3)
    req_version = request.args.get("version", "1.26.3")
    
    print(f"[*] Akses: /{path} | Versi: {req_version}")

    # 1. HANDLING CEK VERSI (Kunci biar gak Download Gagal)
    if "ver.php" in path or "version" in path.lower():
        # Format "Garena Standard" - Pakai pemisah baris \n
        # msg= kosong supaya tidak muncul popup informasi yang mengganggu
        response_text = (
            f"version={req_version}\n"
            "update=0\n"
            "force_update=0\n"
            "download_url=\n"
            "msg="
        )
        
        return Response(
            response_text, 
            mimetype="text/plain",
            headers={
                "Content-Type": "text/plain; charset=utf-8"
            }
        )

    # 2. HANDLING LOGIN (POST)
    if request.method == "POST":
        try:
            res = MajorLogin_pb2.response()
            res.accountId = 1000001
            res.lockRegion = "ID"
            res.notiRegion = "ID"
            res.ipRegion = "ID"
            res.token = "GUEST_LOGIN_TOKEN"
            res.serverUrl = MY_URL
            
            return Response(
                res.SerializeToString(), 
                mimetype="application/x-protobuf"
            )
        except Exception as e:
            print(f"Error Login: {e}")
            return "OK", 200

    return f"Server Online! 🗿"

app = app
