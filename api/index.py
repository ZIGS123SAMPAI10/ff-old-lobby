from flask import Flask, Response

app = Flask(__name__)

# Jalur utama handle root biar Vercel ga eror 404
@app.route("/", methods=["GET", "POST"])
def index():
    return "SERVER WINTERLAND 2018 LIVE JAYA"

# Catch routing spesifik buat /live/ver.php dan /ver.php biar presisi 100%
@app.route("/live/ver.php", methods=["GET", "POST"])
@app.route("/ver.php", methods=["GET", "POST"])
def version_check():
    # Format respons Garena lawas wajib diakhiri \r\n di SETIAP baris termasuk yang paling bawah!
    res_body = (
        "version=1.26.3\r\n"
        "update=0\r\n"
        "force_update=0\r\n"
        "download_url=\r\n"
        "msg=\r\n"
        "md5=\r\n"
        "size=0\r\n"
    )
    
    # Kita paksa kirim response text/plain dengan encoding murni
    response = Response(res_body, mimetype="text/plain")
    # Ditambah header penguat biar engine Unity v1.25.3 lu paham ini data text murni
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return response

# Backup catch-all biar kalau gamenya nembak path gaib lain ga langsung crash 404
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    if "ver.php" in path:
        return version_check()
    return "OK"

if __name__ == "__main__":
    app.run()
