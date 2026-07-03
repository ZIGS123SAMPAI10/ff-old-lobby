from flask import Flask, request, Response
import sys
import os

# Import Protobuf asli Garena
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)

# Tetap kunci di domain Vercel lu sendiri, tanpa redirect ke link baru!
MY_GAME_SERVER = "private89veffold1lb123.vercel.app:443"

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    path_lower = path.lower()

    # 1. HANDLING JALUR VER.PHP
    if "ver.php" in path_lower or "version" in path_lower:
        res_text = "version=1.26.3\nupdate=0\nforce_update=0\ndownload_url=\nmsg="
        return Response(res_text, mimetype="text/plain")

    # 2. HANDLING PROTOBUF LOGIN (Pintu Utama)
    if request.method == "POST" and ("login" in path_lower or "auth" in path_lower):
        try:
            res = MajorLogin_pb2.response()
            res.accountId = 1000001
            res.token = "GUEST_LOGIN_SUCCESS_2018"
            res.serverUrl = MY_GAME_SERVER  # Tetap pancing di Vercel ini
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
                    "Cache-Control": "no-cache, no-store, must-revalidate"
                }
            )
        except Exception as e:
            return f"Error Proto: {str(e)}", 500

    # 3. TRIK SAKRAL: PENANGANAN KONEKSI BERUNTUN (BIAR GAK NGANTUNG)
    # Ini bagian yang dipakai buat nge-jawab kiriman biner pasca-login di jalur yang sama
    if request.method == "POST":
        # Mengambil data biner mentah (payload game) yang dikirim bertubi-tubi oleh APK
        raw_payload = request.data
        
        if raw_payload:
            # Trik: Kembalikan data biner tersebut (Echo Response) dengan format stream murni
            # Ini ngasih tahu engine game kalau server Vercel lu aktif merespon datanya
            return Response(
                raw_payload, 
                mimetype="application/octet-stream",
                headers={
                    "Content-Type": "application/octet-stream",
                    "Cache-Control": "no-cache",
                    "X-Content-Type-Options": "nosniff"
                }
            )
        
        # Jika APK cuma nge-ping kosong, jawab pake JSON kosong status 200 biar gak gantung
        return Response("{}", mimetype="application/json", status=200)

    # Fallback untuk request GET biasa
    return Response("Server Ready", mimetype="text/plain", status=200)

app = app
