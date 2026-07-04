from flask import Flask, request, Response
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)

MY_GAME_SERVER = "private89veffold1lb123.vercel.app:443"

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    path_lower = path.lower()

    # 1. VER.PHP
    if "ver.php" in path_lower or "version" in path_lower:
        return Response("version=1.26.3\nupdate=0\nforce_update=0\ndownload_url=\nmsg=", mimetype="text/plain")

    # 2. LOGIN PROTOBUF - KITA TELANJANGI TANPA HEADER WEB SAMA SEKALI
    if request.method == "POST" and ("login" in path_lower or "auth" in path_lower or "client" in path_lower):
        try:
            res = MajorLogin_pb2.response()
            res.accountId = 1000001
            res.token = "GUEST_LOGIN_SUCCESS_2018"
            res.serverUrl = MY_GAME_SERVER
            res.ipRegion = "ID"
            res.notiRegion = "ID"
            res.lockRegion = "ID"
            res.ttl = 86400  
            res.recommendRegions.append("ID")
            
            binary_data = res.SerializeToString()
            
            # Trik Sakral: Kirim murni data binernya saja, matikan proteksi encoding web
            response = Response(binary_data, status=200, mimetype="application/octet-stream")
            response.headers.clear() # Hapus paksa semua header standard web bawaan Flask
            response.headers["Content-Type"] = "application/octet-stream"
            response.headers["Content-Length"] = str(len(binary_data))
            return response
            
        except Exception as e:
            return str(e), 500

    # 3. PENAMPUNG TRAFFIC LANJUTAN (ECHO STREAM)
    if request.method == "POST":
        raw_payload = request.data
        if raw_payload:
            response = Response(raw_payload, status=200, mimetype="application/octet-stream")
            response.headers.clear()
            response.headers["Content-Type"] = "application/octet-stream"
            response.headers["Content-Length"] = str(len(raw_payload))
            return response

        return Response("", status=200)

    return "Ready", 200

app = app
            
