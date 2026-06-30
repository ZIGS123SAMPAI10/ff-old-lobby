from flask import Flask, request, Response
import sys
import os
import json

# Biar Vercel nemu file proto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)

# Link Server Kamu
MY_URL = "https://private89veffold1lb123.vercel.app"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'] )
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # Ambil angka versi dari game (1.26.3)
    req_version = request.args.get('version', '1.26.3')
    
    # LOG buat kita pantau di Vercel
    print(f"[*] Akses: /{path} | Versi: {req_version}")

    # 1. HANDLING CEK VERSI (Kunci biar gak Download Gagal)
    if "ver.php" in path or "version" in path.lower():
        # Format ini paling standar buat FF Old:
        # Baris 1: Versi yang sama dengan game (biar gak update)
        # Baris 2: Angka 0 (artinya tidak ada update)
        # Baris 3: Kosong (biar gak nyari link download)
        response_text = f"{req_version}\n0\n"
        
        return Response(
            response_text, 
            mimetype='text/plain',
            headers={'Content-Type': 'text/plain; charset=utf-8'}
        )

    # 2. HANDLING LOGIN (POST)
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

    # 3. Respon buat Browser
    return f"Server Online! (Target Versi: {req_version}) 🗿"

app = app
