from flask import Flask, request, Response
import sys
import os

# Import Protobuf yang sudah kamu buat
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import MajorLogin_pb2
except ImportError:
    from . import MajorLogin_pb2

app = Flask(__name__)

# URL Vercel kamu
MY_URL = "https://private89veffold1lb123.vercel.app"

@app.route("/", defaults={"path": ""} )
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    print(f"Game Request: {path}")

    # KUNCI UTAMA: ver.php harus jawab pake Protobuf!
    if "ver.php" in path:
        res = MajorLogin_pb2.response()
        res.accountId = 1001
        res.token = "GUEST_LOGIN_TOKEN"
        res.serverUrl = MY_URL # Kasih tau game harus login ke mana
        res.ipRegion = "ID"
        res.notiRegion = "ID"
        res.lockRegion = "ID"
        
        # Serialize data ke binary
        protobuf_data = res.SerializeToString()
        
        return Response(
            protobuf_data,
            mimetype="application/x-protobuf",
            headers={
                "Content-Type": "application/x-protobuf",
                "Server": "Garena"
            }
        )

    # Respon untuk Login (POST)
    if request.method == "POST":
        res = MajorLogin_pb2.response()
        res.accountId = 1001
        res.token = "GUEST_SUCCESS"
        res.serverUrl = MY_URL
        return Response(res.SerializeToString(), mimetype="application/x-protobuf")

    return "Server Protobuf FF 1.26.3 Aktif! 🗿"

if __name__ == "__main__":
    app.run()
        
