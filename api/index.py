from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return "SERVER WINTERLAND 2018 LIVE JAYA"

@app.route("/live/ver.php", methods=["GET", "POST"])
@app.route("/ver.php", methods=["GET", "POST"])
def version_check():
    client_version = request.args.get("version", "1.26.3")
    
    # 1. Kita susun array string-nya
    lines = [
        f"version={client_version}",
        "update=0",
        "force_update=0",
        "download_url=https://private89veffold1lb123.vercel.app",
        "msg=",
        "md5=00000000000000000000000000000000",
        "size=0"
    ]
    
    # 2. Paksa encode ke bytes murni biner dengan separator \r\n (CRLF) 
    # Biar ga dirusak atau diubah sama sistem server Linux-nya Vercel!
    raw_content = b"\r\n".join([line.encode('utf-8') for line in lines]) + b"\r\n"
    
    # 3. Buat response murni
    response = Response(raw_content, mimetype="text/plain")
    
    # 4. Suntik header sakral: Content-Length wajib dihitung manual biar game tau ukuran aslinya!
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Length"] = str(len(raw_content))
    response.headers["Connection"] = "close"
    
    return response

@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    if "ver.php" in path:
        return version_check()
    return "OK"

if __name__ == "__main__":
    app.run()
