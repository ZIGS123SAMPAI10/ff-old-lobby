from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    # Log ini penting! Cek di Vercel/Termux kamu setelah buka game
    print(f"Game minta file: {path}")

    # 1. Respon Versi (Wajib cuma angka biar gak Download Gagal)
    if "ver" in path:
        return Response("1.26.3", mimetype="text/plain")

    # 2. Respon untuk file lain (notice, msg, login, dll)
    # Kita kasih kosong aja biar dia gak nampilin popup informasi
    return ""

if __name__ == "__main__":
    app.run()
