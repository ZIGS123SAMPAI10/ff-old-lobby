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
    
    print(f"[*] Game Akses Jalur: /{path}")

    # --- HANDLING CEK VERSI (Biar gak Koneksi Error) ---
    if "ver.php" in path or "version" in path.lower():
        # Kita kasih jawaban teks biasa yang disukai FF Old buat cek versi
        # Biasanya formatnya: Version: [versi_terbaru]
        return "Version: 1.25.0\nUpdate: 0\nStatus: OK"

    try:
        # --- HANDLING LOGIN ---
        res = MajorLogin_pb2.response()
        res.accountId = 12345678
        res.lockRegion = "ID"
        res.notiRegion = "ID"
        res.ipRegion = "ID"
        res.token = "SESSION_FIXED_FINAL"
        res.serverUrl = MY_URL
        
        protobuf_data = res.SerializeToString()
        
        # Tambahin 4 byte panjang data (khusus buat login)
        length_prefix = struct.pack('>I', len(protobuf_data))
        final_data = length_prefix + protobuf_data

        return Response(
            final_data, 
            mimetype='application/x-protobuf',
            headers={'Content-Type': 'application/x-protobuf'}
        )

    except Exception as e:
        print(f"Error: {e}")
        return "OK", 200

app = app
        
