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
MY_URL = "https://ffold1lb123.vercel.app"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'] )
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # 1. Respon buat Cek Versi (PENTING!)
    if "ver.php" in path or "version" in path.lower():
        # Kita kasih jawaban standar yang disukai FF 2018
        return "1.25.0" 

    # 2. Respon buat Lobi/Login (POST)
    if request.method == 'POST':
        try:
            # Buat data respons login
            res = MajorLogin_pb2.response()
            res.accountId = 12345678
            res.lockRegion = "ID"
            res.notiRegion = "ID"
            res.ipRegion = "ID"
            res.token = "SESSION_FIXED_FINAL"
            res.serverUrl = MY_URL
            
            # Kirim data MURNI (Tanpa 4-byte prefix buat HTTP)
            return Response(
                res.SerializeToString(), 
                mimetype='application/x-protobuf',
                headers={'Content-Type': 'application/x-protobuf'}
            )
        except Exception as e:
            print(f"Error: {e}")
            return "OK", 200

    # 3. Respon buat Browser
    return "Server Online! 🗿"

app = app
