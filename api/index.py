from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Membaca isi request biner dari APK FF Old lu
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # Kirim header sukses HTTP 200 OK
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        # JALUR UTAMA: Nembak ke alamat localhost.run Termux lu yang aktif!
        # Game bakal ngebaca ini sebagai IP/Host tujuan untuk masuk ke Lobby.
        response_data = {
            "status": 0,
            "message": "SUCCESS",
            "serverUrl": "7c61d239f96d0b.lhr.life",  # Mengarah ke tunnel Termux lu
            "serverPort": 80,                         # Port standar HTTP localhost.run
            "accountId": 12345678,
            "sessionKey": "ZIGS-GAMING-SESSION-TOKEN-2026"
        }
        
        # Kirim balik respon berupa JSON ke APK game FF Old
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return

    def do_GET(self):
        # Jalur cadangan kalau APK lu nge-ping via metode GET
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"FF Old Vercel Auth API Gateway is Running, King!")
        return
        
