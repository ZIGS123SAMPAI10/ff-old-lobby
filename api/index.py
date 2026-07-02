from flask import Flask, Response

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    # Format Garena Asli 2018 - Tanpa Spasi, Pake \r\n
    if "ver.php" in path:
        # Kita susun stringnya dengan sangat hati-hati
        lines = [
            "version=1.26.3",
            "update=0",
            "force_update=0",
            "download_url=",
            "msg=",
            "" # Baris kosong di akhir seringkali wajib ada
        ]
        res_body = "\r\n".join(lines)
        
        return Response(
            res_body,
            status=200,
            mimetype="text/plain",
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "Connection": "keep-alive"
            }
        )

    # Untuk Login (POST)
    if request.method == "POST":
        return "OK"

    return "Server Garena Winterlands 1.26.3 Online! 🗿"

if __name__ == "__main__":
    app.run()
    
