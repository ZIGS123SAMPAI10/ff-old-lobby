from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    print(f"Project Revenger Access: {path}")

    # Trik Bypass Project Revenger: Kasih Error 404
    # Biar game ngerasa server update mati dan langsung lanjut ke Login
    if "ver.php" in path:
        return "Not Found", 404

    # Kalau untuk Login (POST), kita kasih 200 OK
    if request.method == "POST":
        return "OK", 200

    return "Server Project Revenger Aktif! 🗿"

if __name__ == "__main__":
    app.run()
        
