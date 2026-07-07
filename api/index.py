from flask import Flask, request, Response
import requests

app = Flask(__name__)

# ====================================================================
# SESUAIKAN SAMA LINK HIJAU SERVO LU YANG BARU, BRE! 🗿
# ====================================================================
PAGEKITE_DOMAIN = "ffoldprivatserver.serveusercontent.com"
# ====================================================================

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def catch_all(path):
    # Langsung tembak tanpa port 14000 di luar karena via tunnel port 80 HTTP
    url = f"http://{PAGEKITE_DOMAIN}/{path}"
    
    headers = {key: value for (key, value) in request.headers if key.lower() != 'host'}
    
    try:
        response_dari_termux = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            params=request.query_string.decode('utf-8'),
            timeout=8.0
        )
        return Response(
            response_dari_termux.content, 
            status=response_dari_termux.status_code, 
            headers=response_dari_termux.headers.items()
        )
    except requests.exceptions.RequestException as e:
        return f"Gagal tersambung ke backend Termux via Serveo: {e}", 502

app = app
