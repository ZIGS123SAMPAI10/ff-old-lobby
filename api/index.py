from flask import Flask, request, Response
import socket

app = Flask(__name__)

PAGEKITE_DOMAIN = "ffoldprivatserver.serveo.net"
PAGEKITE_PORT   = 14000

@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    try:
        ip_angka = socket.gethostbyname("serveo.net")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(6.0)
        s.connect((ip_angka, PAGEKITE_PORT))
        
        raw_headers = f"{request.method} /{path} HTTP/1.1\r\nHost: {PAGEKITE_DOMAIN}\r\n\r\n".encode()
        raw_body = request.get_data()
        
        s.sendall(raw_headers + raw_body)
        response_data = s.recv(8192)
        s.close()
        
        return Response(response_data, status=200)
    except Exception as e:
        return f"Gagal ke Termux via Serveo: {e}", 502

app = app
