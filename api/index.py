from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    # Log biar kita tau game lagi ngapain
    print(f"Akses: {path} | Versi: {request.args.get('version')}")

    if "ver.php" in path:
        # FORMAT SAKTI GARENA 2018 (Urutan sangat penting!)
        # Kita pakai 1.26.3 sesuai permintaan di log kamu
        res_body = (
            "version=1.26.3\n"
            "update=0\n"
            "force_update=0\n"
            "download_url=\n"
            "msg="
        )
        
        return Response(
            res_body,
            mimetype="text/plain",
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "Server": "Garena"
            }
        )

    # Respon Login (Biar gak stuck)
    if request.method == "POST":
        return "OK"

    return "Server FF 1.26.3 Ready! 🗿"

if __name__ == "__main__":
    app.run()
