import socket
import threading
import time
import secrets
import string
import struct
import sqlite3
import os
import traceback
from flask import Flask, jsonify, request, Response, render_template_string, redirect, url_for

# --- DATABASE HANDLER ---
# Peringatan: SQLite secara lokal tidak persisten di Vercel.
# Data akan hilang setiap kali fungsi di-deploy ulang atau setelah idle.
# Untuk produksi, gunakan database eksternal.
DB_PATH = '/tmp/server.db' # Menggunakan /tmp untuk writeable storage sementara

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"[!] DATABASE ERROR: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                account_id INTEGER UNIQUE NOT NULL,
                nickname TEXT DEFAULT ''
            )
        ''')
        conn.commit()
        conn.close()
        print("[*] Database initialized.")

def get_or_create_user(username, password):
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            if user['password'] == password:
                return dict(user)
            else:
                return None
        else:
            account_id = int(time.time()) % 10000000 + 18400000
            cursor.execute("INSERT INTO users (username, password, account_id) VALUES (?, ?, ?)",
                           (username, password, account_id))
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            return dict(user)
    finally:
        conn.close()

# --- MANUAL PROTOBUF BUILDER (FF v1.29.0 COMPATIBLE) ---
def encode_varint(value):
    out = []
    while value > 127:
        out.append((value & 0x7f) | 0x80)
        value >>= 7
    out.append(value & 0x7f)
    return bytes(out)

def build_login_res(account_id, token, ip, port):
    # Field 1: chat_server (string)
    data = b"\n" + encode_varint(len(f"{ip}:6000")) + f"{ip}:6000".encode()
    # Field 2: notification_channel (string)
    data += b"\x12\x06garena"
    # Field 3: voice_server (string)
    data += b"\x1a" + encode_varint(len(f"{ip}:7000")) + f"{ip}:7000".encode()
    # Field 5: ttl (uint32)
    data += b"(\x80\xa3\x05"
    # Field 7: new_active_region (string)
    data += b"2\x02ID"
    # Field 8: recommend_regions (repeated string)
    data += b":\x02ID"
    # Field 9: server_time (uint32)
    data += b"A" + struct.pack("<I", int(time.time()))
    # Field 12: chat_addr (string) -> IP LOBBY TCP
    lobby_addr = f"{ip}:{port}".encode()
    data += b"J" + encode_varint(len(lobby_addr)) + lobby_addr
    # Field 13: lobby_addr (string) -> IP LOBBY TCP (Backup)
    data += b"R" + encode_varint(len(lobby_addr)) + lobby_addr
    # Field 19: account_id (uint64)
    data += b"\x98\x01" + encode_varint(account_id)
    # Field 20: session_key (string)
    token_bytes = token.encode()
    data += b"\xa2\x01" + encode_varint(len(token_bytes)) + token_bytes

    return data

def build_account_info(account_id, nickname):
    # Field 1: account_id (uint64)
    data = b"\x08" + encode_varint(account_id)
    # Field 2: account_type (uint32)
    data += b"\x10\x02"
    # Field 3: nickname (string)
    nick_bytes = nickname.encode()
    data += b"\x1a" + encode_varint(len(nick_bytes)) + nick_bytes
    # Field 5: region (string)
    data += b"*\x02ID"
    # Field 6: level (uint32)
    data += b"0\x01"
    return data

app = Flask(__name__)

# --- KONFIGURASI ---
# Untuk Vercel, IP ini akan menjadi URL deployment Anda.
# Anda bisa mendapatkan host dari request.host_url atau mengatur ENV variable.
MY_HOST_IP = os.environ.get("MY_HOST_IP", "localhost") # Gunakan variabel lingkungan atau default
HTTP_PORT = int(os.environ.get("PORT", 5000)) # Vercel akan menyediakan port
TCP_PORT = 5034 # Port untuk server TCP

# CURRENT_SESSION tidak akan persisten di Vercel antar request.
# Untuk aplikasi multi-user, Anda perlu menggunakan manajemen sesi yang tepat (misalnya, cookie, database eksternal).
# Untuk tujuan demonstrasi, kita akan menyimpannya sebagai variabel global, tetapi perlu diingat keterbatasannya.
CURRENT_SESSION = {"token": "", "account_id": 0, "username": ""}

# --- HTML LOGIN PAGE ---
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Garena Login</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; padding-top: 50px; }
        .box { background: #1e1e1e; padding: 20px; border-radius: 10px; display: inline-block; border: 1px solid #333; width: 85%; max-width: 320px; }
        input { display: block; width: 90%; padding: 12px; margin: 10px auto; border-radius: 5px; border: none; font-size: 16px; }
        button { width: 98%; padding: 12px; background: #ff4500; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px; }
        h2 { color: #ff4500; }
    </style>
</head>
<body>
    <div class="box">
        <h2>GARENA LOGIN</h2>
        <form action="/login/fb_process" method="POST">
            <input type="text" name="email" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">LOGIN</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/login/facebook", methods=["GET"])
def facebook_login():
    return render_template_string(LOGIN_HTML)

@app.route("/login/fb_process", methods=["POST"])
def fb_process():
    email = request.form.get("email")
    password = request.form.get("password")
    user = get_or_create_user(email, password) # Menggunakan fungsi database asli
    if not user: return "Error", 403

    token = "EAAcX" + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(25))
    CURRENT_SESSION["token"] = token
    CURRENT_SESSION["account_id"] = user["account_id"]
    CURRENT_SESSION["username"] = user["username"]

    print(f"[!] LOGIN: {email} | ID: {user['account_id']}")
    target = f"gop100067://auth/?code={token}"
    return f"<html><script>window.location.href=\\'{target}\\'</script></html>"

@app.route("/oauth/token/exchange", methods=["POST", "GET"])
def token_exchange():
    # Perlu diingat bahwa CURRENT_SESSION tidak persisten di Vercel.
    # Untuk produksi, Anda harus mengambil token dan account_id dari sesi yang sebenarnya (misalnya, dari cookie).
    return jsonify({
        "open_id": str(CURRENT_SESSION["account_id"]),
        "access_token": CURRENT_SESSION["token"],
        "refresh_token": CURRENT_SESSION["token"],
        "expiry_time": int(time.time()) + 360000,
        "platform": 6, "ret": 0, "msg": "success"
    })

@app.route("/live/ver.php", methods=["GET", "POST"])
def ver_php():
    # Di Vercel, request.host akan memberikan domain deployment Anda.
    # Gunakan request.url_root untuk mendapatkan base URL.
    base_url = request.url_root.rstrip('/')
    return jsonify({
        "code": 0, "is_server_open": True, "remote_version": "1.26.3",
        "cdn_url": f"{base_url}/",
        "server_url": f"{base_url}/",
        "core_url": f"{base_url}/"
    } )

@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def main_handler(path):
    full_url = request.url.lower()
    if "ver.php" in full_url or "ver.php" in path: return ver_php()
    if "oauth/login" in full_url: return redirect(url_for("facebook_login"))
    if "token/exchange" in full_url: return token_exchange()

    # Perlu diingat bahwa CURRENT_SESSION tidak persisten di Vercel.
    # Jika account_id atau token tidak ada, ini akan menyebabkan error.
    # Anda perlu memastikan sesi diatur dengan benar sebelum mencapai titik ini.
    # Untuk demonstrasi, kita akan menggunakan nilai default jika tidak ada sesi.
    account_id = CURRENT_SESSION.get("account_id", 18400000)
    token = CURRENT_SESSION.get("token", "DUMMY_TOKEN")
    username = CURRENT_SESSION.get("username", "dummyuser")

    # Di Vercel, request.host akan memberikan domain deployment Anda.
    # Kita akan menggunakan request.host sebagai IP untuk build_login_res.
    ticket = build_login_res(account_id, token, request.host, TCP_PORT)
    return Response(ticket, mimetype="application/octet-stream")

# --- TCP LOBBY ---
def handle_tcp_lobby(client_socket, addr):
    print(f"\n[!!!] CONNECTED FROM {addr} [!!!]")
    try:
        data = client_socket.recv(4096)
        if not data: return

        nickname = ""
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nickname FROM users WHERE account_id = ?", (CURRENT_SESSION["account_id"],))
            row = cursor.fetchone()
            if row: nickname = row['nickname']
            conn.close()

        account_bytes = build_account_info(CURRENT_SESSION["account_id"], nickname)
        cmd_id = 2
        packet_data = struct.pack(">H", cmd_id) + account_bytes
        packet_length = len(packet_data)
        header = struct.pack(">H", packet_length)

        client_socket.sendall(header + packet_data)
        print(f"[+] TCP Lobby Response Sent to ID: {CURRENT_SESSION['account_id']}")

        while True:
            extra_data = client_socket.recv(4096)
            if not extra_data: break
            print(f"[*] TCP Data: {extra_data.hex()}")
    except Exception as e:
        print(f"[!] TCP Error: {e}")
    finally:
        client_socket.close()

def run_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", TCP_PORT))
    server.listen(5)
    print(f"[*] TCP Lobby Active on Port {TCP_PORT}")
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_tcp_lobby, args=(client, addr)).start()

# Vercel akan menjalankan aplikasi Flask secara otomatis menggunakan WSGI.
# Blok `if __name__ == "__main__":` tidak akan dieksekusi di Vercel.
# Namun, untuk eksperimen, kita akan mencoba menjalankan server TCP di sini.
# Ini kemungkinan besar tidak akan berfungsi seperti yang diharapkan di Vercel.
# Untuk menjalankan secara lokal, Anda bisa menambahkan kembali:
# if __name__ == "__main__":
#     init_db()
#     print(f"--- FF v1.29.0 FIXED SERVER v15 ---")
#     threading.Thread(target=lambda: app.run(host="0.0.0.0", port=HTTP_PORT, threaded=True)).start()
#     run_tcp_server()

# Untuk Vercel, Anda hanya perlu mengekspor objek `app`.
# Namun, jika Anda ingin mencoba menjalankan server TCP, Anda bisa memanggilnya di luar blok if __name__.
# Sekali lagi, ini sangat tidak disarankan dan kemungkinan besar tidak akan berfungsi di Vercel.

# Inisialisasi database (akan dibuat di /tmp, tidak persisten)
init_db()

# Jalankan server TCP dalam thread terpisah.
# Ini akan mencoba berjalan, tetapi Vercel mungkin akan menghentikannya.
threading.Thread(target=run_tcp_server).start()

# Untuk Vercel, Anda hanya perlu mengekspor objek `app`.
# Pastikan Anda memiliki file `requirements.txt` yang berisi `Flask` dan `sqlite3` (jika digunakan).
