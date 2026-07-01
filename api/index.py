from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    # Ini buat cek versi (ver.php)
    # Kita kasih respon yang paling simpel: cuma angka versinya
    if "ver" in path or "version" in path:
        return "1.26.3"

    # Ini buat login
    if request.method == "POST":
        # Kita kasih respon sukses sementara biar gak error
        return "OK"

    return "Server FF Old Online! 🗿"

if __name__ == "__main__":
    app.run(debug=True)
