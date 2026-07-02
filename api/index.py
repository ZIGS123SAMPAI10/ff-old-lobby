from flask import Flask, Response

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return "SERVER WINTERLAND 2018 LIVE JAYA"

@app.route("/live/ver.php", methods=["GET", "POST"])
@app.route("/ver.php", methods=["GET", "POST"])
def version_check():
    # Kunci mati di versi kulit luar (1.25.3) biar logika engine Unity
    # ngerasa sinkron sama base APK dan gak nuntut download patch data lagi!
    lines = [
        "version=1.25.3",
        "update=0",
        "force_update=0",
        "download_url=https://private89veffold1lb123.vercel.app",
        "msg=",
        "md5=00000000000000000000000000000000",
        "size=0"
    ]
    
    # Paksa gabungkan pakai biner bytes \r\n biar ga dirusak sistem Linux Vercel
    raw_content = b"\r\n".join([line.encode('utf-8') for line in lines]) + b"\r\n"
    
    response = Response(raw_content, mimetype="text/plain")
    
    # Header proteksi bypass parser biner game lawas
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
