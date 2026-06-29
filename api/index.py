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

# Ganti pake link Vercel kamu
MY_URL = "https://ffold1lb123.vercel.app"

# Trik Sapu Jagat: Nangkep semua jalur (path ) biar gak 404 lagi
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # Kalau dibuka di browser
    if request.method == 'GET':
        return f"Server Online! Jalur yang diakses: /{path} 🗿"
    
    # Kalau diakses sama Game (POST)
    try:
        raw_data = request.get_data()
        
        # Kita coba baca datanya, kalau gagal (misal data FB) kita tetep lanjut
        ff_req = MajorLogin_pb2.request()
        try:
            ff_req.ParseFromString(raw_data)
            acc_id = ff_req.accountid if ff_req.accountid != 0 else 12345678
        except:
            acc_id = 12345678 # ID default buat akun baru/guest

        # Bikin Respons Login Sukses
        ff_res = MajorLogin_pb2.response()
        ff_res.accountId = acc_id
        ff_res.lockRegion = "ID"
        ff_res.token = "GUEST_LOGIN_SUCCESS"
        ff_res.serverUrl = MY_URL
        
        # LOG: Biar kamu tau game lagi akses jalur mana
        print(f"[*] Game akses jalur: /{path} | Respon: Login Sukses")
        
        return Response(ff_res.SerializeToString(), mimetype='application/x-protobuf')
    except Exception as e:
        print(f"[!] Error: {e}")
        return "Internal Error", 500

app = app
        
