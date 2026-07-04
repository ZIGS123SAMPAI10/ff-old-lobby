from flask import Flask, request, redirect, Response

app = Flask(__name__)

# URL PythonAnywhere lu yang baru
PYTHONANYWHERE_SERVER = "https://privateproject45.pythonanywhere.com"

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    path_lower = path.lower()

    # 1. Jalur ver.php atau config teks biasa dihandle langsung di Vercel biar cepet
    if "ver.php" in path_lower or "version" in path_lower:
        # Ini contoh respon versi bawaan game lu, sesuaikan kalau versinya beda
        return Response(
            "version=1.26.3\nupdate=0\nforce_update=0\ndownload_url=\nmsg=", 
            mimetype="text/plain"
        )

    # 2. OPER JALUR (Redirect) untuk Login, Auth, atau data biner game ke PythonAnywhere
    # Menggunakan HTTP 307 supaya Method (POST) dan Body (Biner Protobuf) 
    # dari game dikirim UTUH tanpa diubah/diacak-acak oleh proxy Vercel.
    return redirect(f"{PYTHONANYWHERE_SERVER}/{path}", code=307)

# Handler khusus buat Vercel Serverless
app = app
