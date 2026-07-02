from flask import Flask, Response

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return "SERVER WINTERLAND 2018 LIVE JAYA"

@app.route("/live/ver.php", methods=["GET", "POST"])
@app.route("/ver.php", methods=["GET", "POST"])
def version_check():
    # Format baris teks sakral engine Unity lawas.
    # Kita balikin versi sesuai request game lu tadi (1.26.3) 
    # dengan parameter update dimatikan total.
    lines = [
        "version=1.26.3",
        "update=0",
        "force_update=0",
        "download_url=",
        "msg=",
        "md5=",
        "size=0"
    ]
    
    # Gabungkan dengan biner enter Windows (\r\n) biar ga dirusak server Linux
    raw_content = b"\r\n".join([line.encode('utf-8') for line in lines]) + b"\r\n"
    
    response = Response(raw_content, mimetype="text/plain")
    
    # Kirim header standar murni
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Length"] = str(len(raw_content))
    response.headers["Connection"] = "keep-alive"
    
    return response

@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    if "ver.php" in path:
        return version_check()
    return "OK"

if __name__ == "__main__":
    app.run()
