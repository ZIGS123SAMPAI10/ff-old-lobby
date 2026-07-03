from flask import Flask, request, Response
import sys
import os
import binascii

# Setup path biar bisa baca MajorLogin_pb2
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    # 1. LOGGING PAYLOAD (Buat intip data biner yang kamu minta)
    raw_data = request.get_data()
    if raw_data:
        print(f"\n--- [DATA BINER TERDETEKSI] ---")
        print(f"Path: {path} | Method: {request.method}")
        hex_data = binascii.hexlify(raw_data).decode('utf-8')
        print(f"Hex: {hex_data}")
        
        # Coba decode pake Protobuf Request
        try:
            msg = MajorLogin_pb2.request()
            msg.ParseFromString(raw_data)
            print(f"HASIL DECODE PROTOBUF:\n{msg}")
        except:
            print("Gagal decode sebagai Protobuf Request. Mungkin data dienkripsi.")
        print(f"------------------------------\n")

    # 2. HANDLING VER.PHP (Format Sakti Project Revenger)
    if "ver.php" in path:
        # Format: version|update|force|url|msg
        # Kita pake 1.26.3 sesuai log kamu
        res_text = "1.26.3|0|0||"
        return Response(res_text, mimetype="text/plain")

    # 3. HANDLING LOGIN (POST) - Pake Protobuf Biar Gak Loading Lama
    if request.method == "POST":
        try:
            res = MajorLogin_pb2.response()
            res.accountId = 1000001
            res.token = "GUEST_OK_REV"
            res.serverUrl = "https://private89veffold1lb123.vercel.app"
            res.ipRegion = "ID"
            res.notiRegion = "ID"
            res.lockRegion = "ID"
            res.ttl = 86400
            
            return Response(
                res.SerializeToString( ), 
                mimetype="application/x-protobuf"
            )
        except Exception as e:
            print(f"Error Login: {e}")
            return "OK"

    return "Server Project Revenger Decoder Active! 🗿"

if __name__ == "__main__":
    app.run()
    
