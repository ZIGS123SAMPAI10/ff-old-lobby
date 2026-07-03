from flask import Flask, request, Response
import sys
import os
import binascii

# Setup path agar bisa baca MajorLogin_pb2
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    # Ambil data biner mentah dari request
    raw_data = request.get_data()
    
    print(f"\n--- [DEBUG] REQUEST MASUK ---")
    print(f"Path: {path}")
    print(f"Method: {request.method}")
    
    if raw_data:
        # 1. Print Payload dalam format HEX (Biar bisa dibandingin sama SS)
        hex_payload = binascii.hexlify(raw_data).decode('utf-8')
        print(f"Raw Hex: {hex_payload}")
        
        # 2. Coba Decode pake Protobuf MajorLogin
        try:
            # Kita coba pake 'request' message dari proto kamu
            req_msg = MajorLogin_pb2.request()
            req_msg.ParseFromString(raw_data)
            print(f"HASIL DECODE PROTOBUF:\n{req_msg}")
        except Exception as e:
            print(f"Gagal decode Protobuf: {e}")
            print("Mungkin data dienkripsi atau formatnya bukan MajorLogin.request")
    else:
        print("Tidak ada payload biner (Request Kosong)")
    
    print(f"-----------------------------\n")

    # Tetap kasih respon ver.php supaya game gak langsung mati
    if "ver.php" in path:
        # Kita kasih respon dummy sementara
        return "1.26.3"

    return "Logger Active! 🗿", 200

if __name__ == "__main__":
    app.run()
    
