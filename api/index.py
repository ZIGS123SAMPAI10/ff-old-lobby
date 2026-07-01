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
    print(f"[*] Akses: /{path}")

    # 1. HANDLING CEK VERSI (Format paling stabil untuk FF 1.26.3)
    if "ver.php" in path or "version" in path.lower():
        # Pakai format yang sangat sederhana tanpa spasi
        # Kita paksa versinya ke 1.26.3
        response_text = "version=1.26.3\nupdate=0\nforce_update=0\ndownload_url=\nmsg="
        
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
