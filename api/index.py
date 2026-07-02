from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return "SERVER WINTERLAND 2018 LIVE JAYA"

@app.route("/live/ver.php", methods=["GET", "POST"])
@app.route("/ver.php", methods=["GET", "POST"])
def version_check():
    # Mengambil versi langsung dari request game secara dinamis (biar sinkron 100%)
    client_version = request.args.get("version", "1.26.3")
    
    # Format text murni Garena lawas. Gunakan join biar ga ada whitespace/spasi gaib dari Python
    lines = [
        f"version={client_version}",
        "update=0",
        "force_update=0",
        "download_url=https://private89veffold1lb123.vercel.app",
        "msg=",
        "md5=00000000000000000000000000000000",
        "size=0"
    ]
    
    # Gabungkan dengan \r\n di setiap baris, DAN pastikan ada \r\n di akhir baris paling bawah!
    res_body = "\r\n".join(lines) + "\r\n"
    
    # Buat response murni text/plain tanpa embel-embel HTML
    response = Response(res_body, mimetype="text/plain")
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return response

@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    if "ver.php" in path:
        return version_check()
    return "OK"

if __name__ == "__main__":
    app.run()
