from flask import Flask, Response

app = Flask(__name__)

# Fungsi XOR Cipher standar Garena Lawas
def garena_xor_encrypt(data_string, key="garena"):
    encrypted = bytearray()
    for i in range(len(data_string)):
        # Setiap karakter teks di-XOR dengan karakter kunci secara berulang
        encrypted.append(ord(data_string[i]) ^ ord(key[i % len(key)]))
    return bytes(encrypted)

@app.route("/", methods=["GET", "POST"])
def index():
    return "SERVER WINTERLAND 2018 LIVE JAYA"

@app.route("/live/ver.php", methods=["GET", "POST"])
@app.route("/ver.php", methods=["GET", "POST"])
def version_check():
    # 1. Buat teks respon mentah dengan format enter Windows (\r\n)
    lines = [
        "version=1.26.3",
        "patch_version=1.26.3",
        "update=0",
        "force_update=0",
        "download_url=",
        "md5=",
        "size=0",
        "msg="
    ]
    raw_text = "\r\n".join(lines) + "\r\n"
    
    # 2. Enkripsi teksnya secara real-time pake kunci "garena"
    encrypted_bytes = garena_xor_encrypt(raw_text, key="garena")
    
    # 3. Kirim data enkripsi mentah ke game FF
    response = Response(encrypted_bytes, mimetype="text/plain")
    
    # Header steril wajib biar ga dirusak proxy Vercel
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Length"] = str(len(encrypted_bytes))
    response.headers["Connection"] = "keep-alive"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    
    return response

@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    if "ver.php" in path:
        return version_check()
    return "OK"

if __name__ == "__main__":
    app.run()
    
