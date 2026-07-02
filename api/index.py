from flask import Flask, Response

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    # Respon ini pake format Garena 2018 yang paling lengkap
    # Kita pake \r\n (Windows Style) buat jaga-jaga
    if "ver.php" in path:
        res_body = (
            "version=1.26.3\r\n"
            "update=0\r\n"
            "force_update=0\r\n"
            "download_url=\r\n"
            "msg=\r\n"
            "md5=\r\n"
            "size=0"
        )
        return Response(res_body, mimetype="text/plain")

    return "OK"

if __name__ == "__main__":
    app.run()
    
