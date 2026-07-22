import socket
import threading
import time
import secrets
import string
import struct
import sqlite3
import os
import base64
from flask import Flask, jsonify, request, Response, render_template_string, redirect, url_for, make_response

# --- DATABASE HANDLER ---
# Di Vercel, hanya direktori /tmp yang bisa ditulisi
DB_PATH = '/tmp/server.db'

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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                account_id INTEGER,
                token TEXT,
                username TEXT
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

def save_session_to_db(account_id, token, username):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO sessions (id, account_id, token, username) VALUES (1, ?, ?, ?)",
                       (account_id, token, username))
        conn.commit()
        conn.close()

def load_session_from_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    return {"token": "", "account_id": 0, "username": ""}

# --- MANUAL PROTOBUF BUILDER (FF v1.25.3 COMPATIBLE - ASLI TEMUAN ANDA) ---
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
    # Field 12: chat_addr (string)
    lobby_addr = f"{ip}:{port}".encode()
    data += b"J" + encode_varint(len(lobby_addr)) + lobby_addr
    # Field 13: lobby_addr (string)
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

# --- HTML PUBLIC STATUS PAGE (TAMBAHAN KHUSUS UTK ADMIN / IS-A.DEV CHECKER) ---
PUBLIC_HOME_HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FF Old Server Service</title>
    <style>
        body {
            background-color: #0d1117;
            color: #c9d1d9;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 30px;
            width: 320px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }
        h2 { color: #58a6ff; margin-top: 0; font-size: 18px; }
        .status-badge {
            background-color: rgba(46, 160, 67, 0.15);
            color: #3fb950;
            border: 1px solid rgba(63, 185, 80, 0.4);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
            margin: 15px 0;
        }
        p { color: #8b949e; font-size: 12px; margin-bottom: 0; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🔥 FF Old Server API</h2>
        <div class="status-badge">● SERVICE ONLINE</div>
        <p>Game Backend Endpoint Active (v1.25.3)</p>
    </div>
</body>
</html>
"""

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
    user = get_or_create_user(email, password)
    if not user: return "Error", 403

    token = "EAAcX" + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(25))
    
    save_session_to_db(user["account_id"], token, user["username"])

    print(f"[!] LOGIN: {email} | ID: {user['account_id']}")
    target = f"gop100067://auth/?code={token}"
    
    response = make_response(redirect(target, code=302))
    return response

@app.route("/oauth/token/exchange", methods=["POST", "GET"])
@app.route("/oauth/token/facebook/exchange", methods=["POST"])
def token_exchange():
    session = load_session_from_db()
    return jsonify({
        "open_id": str(session["account_id"]),
        "access_token": session["token"],
        "refresh_token": session["token"],
        "expiry_time": int(time.time()) + 360000,
        "platform": 6, "ret": 0, "msg": "success"
    })

@app.route("/live/ver.php", methods=["GET", "POST"])
def ver_php():
    host = request.host
    return jsonify({
        "code": 0, "is_server_open": True, "remote_version": "1.25.3",
        "cdn_url": f"http://{host}/",
        "server_url": f"http://{host}/",
        "core_url": f"http://{host}/"
    })

@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def main_handler(path):
    # TAMBAHAN BANTENG: Jika admin/browser buka root "/" dengan method GET, tampilkan UI web rapi
    if request.method == "GET" and (path == "" or path == "/"):
        return render_template_string(PUBLIC_HOME_HTML)

    full_url = request.url.lower()
    
    if "oauth/login" in full_url or "dialog/oauth" in full_url:
        return facebook_login()
        
    if "ver.php" in full_url or "ver.php" in path: return ver_php()
    if "token/exchange" in full_url or "token/facebook/exchange" in full_url: return token_exchange()

    session = load_session_from_db()
    ticket = build_login_res(session["account_id"], session["token"], request.host, TCP_PORT)
    return Response(ticket, mimetype="application/octet-stream")

init_db()
        
