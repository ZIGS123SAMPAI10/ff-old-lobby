from flask import Flask, request, Response
import requests

app = Flask(__name__)

# ====================================================================
# VARIABEL LINK DAN PORT LU TETEP AMAN SAMA KAYA KEMARIN BRE! 🗿
# ====================================================================
PAGEKITE_DOMAIN = "ffoldprivatserver.serveo.net"
PAGEKITE_PORT   = 14000
# ====================================================================

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def catch_all(path):
    # Rakit URL lengkap beserta parameter ?version=... bawaan game FF lu secara otomatis
    url = f"http://{PAGEKITE_DOMAIN}:{PAGEKITE_PORT}/{path}"
    
    # Ambil headers bawaan game dan bersihkan biar gak tabrakan di proxy Vercel
    headers = {key: value for (key, value) in request.headers if key.lower() != 'host'}
    
    try:
        # Oper request secara utuh dan sempurna (Query params, data biner, sikat semua!)
        response_dari_termux = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            params=request.query_string.decode('utf-8'), # <--- INI KUNCI BIAR PARAMETER ?VERSION KAGAK ILANG!
            timeout=8.0
        )
        
        # Kembalikan jawaban ver.php dari Termux lu utuh ke APK Free Fire
        return Response(
            response_dari_termux.content, 
            status=response_dari_termux.status_code, 
            headers=response_dari_termux.headers.items()
        )
        
    except requests.exceptions.RequestException as e:
        return f"Gagal tersambung ke backend Termux via Serveo: {e}", 502

app = app
