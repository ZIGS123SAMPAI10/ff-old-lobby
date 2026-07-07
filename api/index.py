from flask import Flask, request, Response
import requests

app = Flask(__name__)

# ====================================================================
# DOMAIN SERVO LU YANG SUDAH TERKUNCI (TANPA HTTPS://)
# ====================================================================
PAGEKITE_DOMAIN = "ffoldprivatserver.serveusercontent.com"
# ====================================================================

@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def catch_all(path):
    # Wajib pakai https:// karena tunnel Serveo lu berjalan di HTTPS
    url = f"https://{PAGEKITE_DOMAIN}/{path}"
    
    # Ambil semua headers dari game, tapi buang header 'host' asli Vercel
    headers = {key: value for (key, value) in request.headers if key.lower() != 'host'}
    
    try:
        # Kirim data dari Vercel menuju terowongan Serveo di HP lu
        response_dari_termux = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            params=request.query_string.decode('utf-8'),
            timeout=10.0  # Gua naikin jadi 10 detik biar gak gampang RTO
        )
        
        # Balikin respon dari Termux lu langsung ke game FF Old
        return Response(
            response_dari_termux.content, 
            status=response_dari_termux.status_code, 
            headers=response_dari_termux.headers.items()
        )
        
    except requests.exceptions.Timeout:
        return f"Eror: Koneksi ke Termux Timeout (RTO). Pastikan SSH Serveo di HP lu masih aktif, bre!", 504
    except requests.exceptions.ConnectionError as ce:
        return f"Eror: Gagal tersambung ke Serveo/Termux. Detail: {str(ce)}", 502
    except requests.exceptions.RequestException as e:
        return f"Eror sistem proxy Vercel: {str(e)}", 500

# Pengaman buat deployment Vercel
app = app
