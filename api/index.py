from flask import Flask, request, Response
import sys
import os

# TRICK: Biar Vercel bisa nemu file MajorLogin_pb2.py di folder api
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def lobby():
    # Kalau dibuka di browser (GET)
    if request.method == 'GET':
        return "Server Online! (Garis miring sudah dibersihkan) 🗿"
    
    # Kalau diakses sama Game (POST)
    try:
        raw_data = request.get_data()
        ff_req = MajorLogin_pb2.request()
        ff_req.ParseFromString(raw_data)
        
        # Log ini bakal muncul di Dashboard Vercel > Logs
        print(f"Login Masuk: {ff_req.nickname}")

        ff_res = MajorLogin_pb2.response()
        ff_res.accountId = ff_req.accountid
        ff_res.lockRegion = "ID"
        ff_res.token = "SESSION_FIXED_FINAL"
        
        # SAKTI: Hapus garis miring (/) di paling ujung link biar game nggak bingung
        ff_res.serverUrl = request.url_root.rstrip('/')
        
        return Response(ff_res.SerializeToString(), mimetype='application/x-protobuf')
    except Exception as e:
        print(f"Error: {e}")
        return "Internal Error", 500

# Wajib buat Vercel
app = app
