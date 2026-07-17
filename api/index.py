import socket
import threading
import time
import secrets
import string
import struct
import sqlite3
import os
import json
import traceback
from flask import Flask, jsonify, request, Response, render_template_string, redirect, url_for, make_response

# --- DATABASE HANDLER ---
# Di Vercel, kita gunakan /tmp agar bisa ditulisi.
DB_PATH = '/tmp/server.db'
SESSION_FILE = '/tmp/session.json'

def save_session(data):
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump(data, f)
    except: pass

def load_session():
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
    except: pass
    return {"token": "", "account_id": 0, "username": ""}

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

# --- MANUAL PROTOBUF BUILDER (FF v1.29.0 COMPATIBLE - ASLI) ---
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
TCP_PORT = 5034

# --- HTML LOGIN PAGE ---
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
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
    user = get_or_create_user(email, password)
    if not user: return "Error", 403

    token = "EAAcX" + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(25))
    
    # Simpan sesi agar tidak hilang di Vercel
    session_data = {"token": token, "account_id": user["account_id"], "username": user["username"]}
    save_session(session_data)

    print(f"[!] LOGIN: {email} | ID: {user['account_id']}")
    target = f"gop100067://auth/?code={token}"
    return f"<html><script>window.location.href='{target}';</script></html>"

@app.route("/oauth/token/exchange", methods=["POST", "GET"])
def token_exchange():
    session = load_session()
    return jsonify({
        "open_id": str(session["account_id"]),
        "access_token": session["token"],
        "refresh_token": session["token"],
        "expiry_time": int(time.time()) + 360000,
        "platform": 6, "ret": 0, "msg": "success"
    })

@app.route("/live/ver.php", methods=["GET", "POST"])
def ver_php():
    # Gunakan request.host agar dinamis di Vercel
    return jsonify({
        "code": 0, "is_server_open": True, "remote_version": "1.26.3",
        "cdn_url": f"http://{request.host}/",
        "server_url": f"http://{request.host}/",
        "core_url": f"http://{request.host}/"
    } )

@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def main_handler(path):
    full_url = request.url.lower()
    if "ver.php" in full_url or "ver.php" in path: return ver_php()
    
    # PERBAIKAN: Kirim HTML langsung tanpa redirect agar tidak STUCK
    if "oauth/login" in full_url or "dialog/oauth" in full_url: 
        res = make_response(LOGIN_HTML)
        res.headers['Content-Type'] = 'text/html; charset=utf-8'
        return res
        
    if "token/exchange" in full_url: return token_exchange()

    session = load_session()
    ticket = build_login_res(session["account_id"], session["token"], request.host, TCP_PORT)
    return Response(ticket, mimetype="application/octet-stream")

# --- TCP LOBBY ---
def handle_tcp_lobby(client_socket, addr):
    try:
        data = client_socket.recv(4096)
        if not data: return
        session = load_session()
        
        nickname = ""
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nickname FROM users WHERE account_id = ?", (session["account_id"],))
            row = cursor.fetchone()
            if row: nickname = row['nickname']
            conn.close()

        account_bytes = build_account_info(session["account_id"], nickname)
        packet_data = struct.pack(">H", 2) + account_bytes
        header = struct.pack(">H", len(packet_data))
        client_socket.sendall(header + packet_data)
    except: pass
    finally: client_socket.close()

def run_tcp_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", TCP_PORT))
        server.listen(5)
        while True:
            client, addr = server.accept()
            threading.Thread(target=handle_tcp_lobby, args=(client, addr)).start()
    except: pass

# Startup
init_db()
if not os.environ.get('VERCEL'):
    threading.Thread(target=run_tcp_server, daemon=True).start()
