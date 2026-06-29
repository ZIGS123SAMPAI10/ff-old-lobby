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
    # --- LOGGING DETAIL (Cek di Dashboard Vercel > Logs) ---
    print(f"[*] Game Akses Jalur: /{path}")
    
    # 1. HANDLING CEK VERSI (/live/ver.php)
    # Format ini adalah format standar PHP Garena tahun 2018
    if "ver.php" in path or "version" in path.lower():
        # Baris 1: Versi Game
        # Baris 2: Flag Update (0 = Tidak ada update)
        # Baris 3: Link Update (none = Tidak ada link)
        response_text = "1.25.3\n0\nnone"
        
        return Response(
            response_text, 
            mimetype="text/plain",
            headers={'Content-Type': 'text/plain; charset=utf-8'}
        )

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
            
            # Kita kirim data murni Protobuf (Seringkali FF 2018 lebih suka ini via HTTP)
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
