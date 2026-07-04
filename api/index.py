from flask import Flask, request, Response
from flask_sock import Sock
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)
# Inisialisasi Websocket Handler
sock = Sock(app)

MY_GAME_SERVER = "private89veffold1lb123.vercel.app:443"

# --- JALUR 1: HANDLER WEBSOCKET UTAMA (BYPASS PIPELINE VERCEL) ---
@sock.route('/ws-login')
def ws_login_handler(ws):
    """
    Begitu game dialihkan ke sini, koneksi otomatis berubah jadi WebSocket Stream.
    Vercel tidak akan ikut campur lagi dengan struktur datanya.
    """
    while True:
        # Terima data biner mentah dari game
        data = ws.receive()
        if not data:
            break
        
        try:
            # Susun data balasan Protobuf pakai rumus MajorLogin_pb2
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
            
            # Tembak langsung data binernya lewat terowongan WebSocket
            ws.send(binary_data)
        except Exception as e:
            print(f"Error di WS: {e}")
            break

# --- JALUR 2: HTTP REGULER (UNTUK CEK VERSI & UPGRADE PROTOKOL) ---
@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    path_lower = path.lower()

    # 1. Handle ver.php tetap pakai teks biasa (karena gak bikin eror)
    if "ver.php" in path_lower or "version" in path_lower:
        return Response("version=1.26.3\nupdate=0\nforce_update=0\ndownload_url=\nmsg=", mimetype="text/plain")

    # 2. Pengalihan Otomatis ke Jalur Websocket jika ada request Login
    if "login" in path_lower or "auth" in path_lower or "client" in path_lower:
        # Kirim status 101 untuk memaksa koneksi Vercel melakukan Upgrade Protocol ke Websocket
        return Response(
            status=101,
            headers={
                "Upgrade": "websocket",
                "Connection": "Upgrade",
                "Location": f"wss://{MY_GAME_SERVER}/ws-login"
            }
        )

    return "Ready", 200

app = app
    
