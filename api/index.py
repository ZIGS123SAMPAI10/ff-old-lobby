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
    # Ambil versi dari game (1.26.3)
    req_version = request.args.get('version', '1.26.3')
    
    print(f"[*] Akses: /{path} | Versi: {req_version}")

    # 1. HANDLING CEK VERSI (Versi JSON Pro)
    if "ver.php" in path or "version" in path.lower():
        # Format JSON ini sering diminta FF 1.26.x buat bypass update
        version_data = {
            "version": req_version,
            "status": 0,
            "url": "",
            "force": False,
            "maintance": False,
            "msg": ""
        }
        return Response(
            json.dumps(version_data), 
            mimetype='application/json',
            headers={'Content-Type': 'application/json; charset=utf-8'}
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

    return f"Server Online! 🗿"

app = app
            
