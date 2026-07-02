from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return "SERVER WINTERLAND 2018 LIVE JAYA"

@app.route("/live/ver.php", methods=["GET", "POST"])
@app.route("/ver.php", methods=["GET", "POST"])
def version_check():
    client_version = request.args.get("version", "1.26.3")
    
    # Kita ubah format variabelnya pake HURUF BESAR SEMUA (All Caps)
    # Ini format standar parser C++ engine game lawas biar ga gagal baca!
    lines = [
        f"VERSION={client_version}",
        "UPDATE=0",
        "FORCE=0",
        "URL=https://private89veffold1lb123.vercel.app",
        "MSG=",
        "MD5=00000000000000000000000000000000",
        "SIZE=0"
    ]
    
    res_body = "\r\n".join(lines) + "\r\n"
    
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
