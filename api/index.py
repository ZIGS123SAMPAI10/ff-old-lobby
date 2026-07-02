from flask import Flask, Response

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return "SERVER WINTERLAND 2018 LIVE JAYA"

@app.route("/live/ver.php", methods=["GET", "POST"])
@app.route("/ver.php", methods=["GET", "POST"])
def version_check():
    # download_url langsung ngarah ke server Vercel lu sendiri biar gamenya ga nganggep kosong/corrupt
    res_body = (
        "version=1.26.3\r\n"
        "update=0\r\n"
        "force_update=0\r\n"
        "download_url=https://private89veffold1lb123.vercel.app\r\n"
        "msg=\r\n"
        "md5=00000000000000000000000000000000\r\n"
        "size=0\r\n"
    )
    
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
