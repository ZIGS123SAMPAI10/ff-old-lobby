from flask import Flask, request, Response
import socket

app = Flask(__name__)

# ====================================================================
# TARGET OPERAN: LANGSUNG KE JEMBATAN SERVEO TERMUX (PAS PORT 14000)
# ====================================================================
PAGEKITE_DOMAIN = "serveo.net"
PAGEKITE_PORT   = 14000
# ====================================================================

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    try:
        # 1. Ambil IP Angka dari Serveo secara real-time
        ip_angka = socket.gethostbyname(PAGEKITE_DOMAIN)
        
        # 2. Buka pipa socket TCP langsung ke Termux via Serveo
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(6.0)
        s.connect((ip_angka, PAGEKITE_PORT))
        
        # 3. Ambil data mentah dari game (GET ver.php atau POST biner login, oper semua!)
        # Kita rakit ulang request HTTP/Biner aslinya agar dibaca utuh oleh Termux
        raw_headers = f"{request.method} /{path} HTTP/1.1\r\nHost: {PAGEKITE_DOMAIN}\r\n\r\n".encode()
        raw_body = request.get_data()
        
        # Tembakkan langsung paketnya menuju Termux
        s.sendall(raw_headers + raw_body)
        
        # 4. Ambil jawaban dari Termux, lalu oper balik ke game FF lu
        response_data = s.recv(8192)
        s.close()
        
        return Response(response_data, status=200)
        
    except Exception as e:
        return f"Gagal tersambung ke backend Termux via Serveo: {e}", 502

app = app
