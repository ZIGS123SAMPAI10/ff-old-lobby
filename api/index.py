from flask import Flask, request, Response
import socket

app = Flask(__name__)

# ====================================================================
# LINK DAN PORT ASLI LU, KAGAK GUA SENTUH ATAU UBAH STRUKTURNYA BRE! 🗿
# ====================================================================
PAGEKITE_DOMAIN = "ffoldprivatserver.serveo.net"
PAGEKITE_PORT   = 14000
# ====================================================================

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    try:
        # 1. Ambil IP Angka dari Serveo secara real-time lewat domain utamanya
        ip_angka = socket.gethostbyname("serveo.net")
        
        # 2. Buka pipa socket TCP langsung ke Termux via Serveo
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(6.0)
        s.connect((ip_angka, PAGEKITE_PORT))
        
        # 3. Ambil data mentah dari game (GET ver.php atau POST biner login, oper semua!)
        # Host header otomatis disamain pake variabel PAGEKITE_DOMAIN di atas
        raw_headers = f"{request.method} /{path} HTTP/1.1\r\nHost: {PAGEKITE_DOMAIN}\r\n\r\n".encode()
        raw_body = request.get_data()
        
        # Tembakkan langsung paketnya menuju Termux lu
        s.sendall(raw_headers + raw_body)
        
        # 4. Ambil jawaban dari Termux, lalu oper balik ke game FF lu
        response_data = s.recv(8192)
        s.close()
        
        return Response(response_data, status=200)
        
    except Exception as e:
        return f"Gagal tersambung ke backend Termux via Serveo: {e}", 502

app = app
