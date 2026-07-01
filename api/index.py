from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    # Kita ambil versi yang dikirim game, kalau gak ada kita pake 1.25.3
    v_game = request.args.get("version", "1.25.3")
    
    print(f"Game akses: {path} | Versi Game: {v_game}")

    if "ver" in path or "version" in path:
        # Trik SAKTI: Kita balikin versi yang sama dengan yang diminta game
        # Jadi game bakal mikir dia sudah versi terbaru (Gak perlu update)
        # Format: version=... (pake baris baru)
        res_text = f"version={v_game}\nupdate=0\nforce_update=0\ndownload_url=\nmsg="
        
        return Response(res_text, mimetype="text/plain")

    if request.method == "POST":
        return "OK"

    return "Server Sinkron FF Aktif! 🗿"

if __name__ == "__main__":
    app.run()
