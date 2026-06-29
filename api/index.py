from flask import Flask, request, Response
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)
MY_URL = "https://ffold1lb123.vercel.app"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'] )
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # --- LOGGING UNTUK DEBUG ---
    print(f"[*] Akses Jalur: /{path} | Method: {request.method}")
    
    # 1. HANDLING CEK VERSI (/live/ver.php)
    if "ver.php" in path or "version" in path.lower():
        # Kita coba format 'Legacy' yang paling ampuh buat FF 2018
        # Format: [Versi]|[Update_Flag]|[URL_Update]
        return Response("1.25.0|0|none", mimetype="text/plain")

    # 2. HANDLING LOGIN & LOBBY (POST)
    if request.method == 'POST':
        try:
            res = MajorLogin_pb2.response()
            res.accountId = 12345678
            res.lockRegion = "ID"
            res.notiRegion = "ID"
            res.ipRegion = "ID"
            res.token = "GUEST_SUCCESS_FINAL"
            res.serverUrl = MY_URL
            
            return Response(
                res.SerializeToString(), 
                mimetype="application/x-protobuf",
                headers={'Content-Type': 'application/x-protobuf'}
            )
        except Exception as e:
            print(f"Error Login: {e}")
            return "OK", 200

    return "Server Online! 🗿"

app = app
