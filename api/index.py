from flask import Flask, request, Response
import sys
import os

# Biar Vercel nemu file proto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)

# --- LINK BARU KAMU ---
MY_URL = "https://private89veffold1lb123.vercel.app"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'] )
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # Ambil angka versi dari game (biar gak Download Gagal)
    req_version = request.args.get('version', '1.26.3')
    
    print(f"[*] Game Akses: /{path} | Versi: {req_version}")

    # 1. HANDLING CEK VERSI
    if "ver.php" in path or "version" in path.lower():
        # Jawab pake versi yang diminta game biar dia seneng
        return f"{req_version}\n0\nnone"

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
                mimetype='application/x-protobuf',
                headers={'Content-Type': 'application/x-protobuf'}
            )
        except Exception as e:
            print(f"Error Login: {e}")
            return "OK", 200

    return f"Server Online! (Link: {MY_URL}) 🗿"

app = app
