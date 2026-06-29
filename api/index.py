from flask import Flask, request, Response
import struct
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
    if request.method == 'GET':
        return "Server Online! 🗿"
    
    # LOG: Liat di Vercel Dashboard > Logs
    print(f"[*] Game Akses Jalur: /{path}")

    try:
        # 1. Bikin data respons login
        res = MajorLogin_pb2.response()
        res.accountId = 12345678
        res.lockRegion = "ID"
        res.notiRegion = "ID"
        res.ipRegion = "ID"
        res.token = "GUEST_SUCCESS_FIX"
        res.serverUrl = MY_URL
        res.ttl = 3600 # Tambahin waktu expired token
        
        # 2. Serialisasi jadi binary
        protobuf_data = res.SerializeToString()
        
        # --- TRIK RAHASIA FF 2018 ---
        # Tambahin 4 byte di depan yang isinya panjang data (Big Endian)
        # Beberapa versi FF Old butuh ini biar gak 'Connection Error'
        length_prefix = struct.pack('>I', len(protobuf_data))
        final_data = length_prefix + protobuf_data
        # ----------------------------

        return Response(
            final_data, 
            mimetype='application/x-protobuf',
            headers={
                'Content-Type': 'application/x-protobuf',
                'Server': 'Garena' # Pura-pura jadi server Garena
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        return "OK", 200

app = app
