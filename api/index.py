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

# Link Server Kamu
MY_URL = "https://private89veffold1lb123.vercel.app"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'] )
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # Ambil angka versi dari game (1.26.3)
    req_version = request.args.get('version', '1.26.3')
    
    # LOG buat kita pantau
    print(f"[*] Akses: /{path} | Versi: {req_version}")

    # 1. HANDLING CEK VERSI (Biar gak Download Gagal)
    if "ver.php" in path or "version" in path.lower():
        # KUNCI: Kembalikan HANYA angka versi tanpa spasi atau baris baru (\n)
        # Ini format paling murni yang diminta FF 1.26.x
        return Response(
            req_version, 
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
            
            # Kirim data murni Protobuf
            return Response(
                res.SerializeToString(), 
                mimetype='application/x-protobuf',
                headers={'Content-Type': 'application/x-protobuf'}
            )
        except Exception as e:
            print(f"Error Login: {e}")
            return "OK", 200

    return f"Server Online! 🗿"

app = app
