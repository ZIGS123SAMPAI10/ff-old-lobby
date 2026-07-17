import socket
import threading
import time
import secrets
import string
import struct
import sqlite3
import os
import traceback
from flask import Flask, jsonify, request, Response, render_template_string, redirect, url_for, make_response

# --- DATABASE HANDLER ---
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
                id INTEGER PRIMARY KEY,
                token TEXT,
                account_id INTEGER
            )
        ''')
        conn.commit()
        conn.close()
        print("[*] Database initialized.")

def save_session_to_db(account_id, token):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO sessions (id, token, account_id) VALUES (1, ?, ?)", (token, account_id))
        conn.commit()
        conn.close()

def load_session_from_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        if row: return {"token": row['token'], "account_id": row['account_id']}
    return {"token": "", "account_id": 0}

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
    data = b"\n" + encode_varint(len(f"{ip}:6000")) + f"{ip}:6000".encode()
    data += b"\x12\x06garena"
    data += b"\x1a" + encode_varint(len(f"{ip}:7000")) + f"{ip}:7000".encode()
    data += b"(\x80\xa3\x05"
    data += b"2\x02ID"
    data += b":\x02ID"
    data += b"A" + struct.pack("<I", int(time.time()))
    lobby_addr = f"{ip}:{port}".encode()
    data += b"J" + encode_varint(len(lobby_addr)) + lobby_addr
    data += b"R" + encode_varint(len(lobby_addr)) + lobby_addr
    data += b"\x98\x01" + encode_varint(account_id)
    token_bytes = token.encode()
    data += b"\xa2\x01" + encode_varint(len(token_bytes)) + token_bytes
    return data

def build_account_info(account_id, nickname):
    data = b"\x08" + encode_varint(account_id)
    data += b"\x10\x02"
    nick_bytes = nickname.encode()
    data += b"\x1a" + encode_varint(len(nick_bytes)) + nick_bytes
    data += b"*\x02ID"
    data += b"0\x01"
    return data

app = Flask(__name__)
TCP_PORT = 5034

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
    
    # Simpan ke Database SQLite agar tidak hilang di Vercel
    save_session_to_db(user["account_id"], token)

    print(f"[!] LOGIN: {email} | ID: {user['account_id']}")
    target = f"gop100067://auth/?code={token}"
    return f"<html><script>window.location.href='{target}';</script></html>"

@app.route("/oauth/token/exchange", methods=["POST", "GET"])
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
    
    if "oauth/login" in full_url or "dialog/oauth" in full_url: 
        res = make_response(LOGIN_HTML)
        res.headers['Content-Type'] = 'text/html; charset=utf-8'
        return res
        
    if "token/exchange" in full_url: return token_exchange()

    session = load_session_from_db()
    ticket = build_login_res(session["account_id"], session["token"], request.host, TCP_PORT)
    return Response(ticket, mimetype="application/octet-stream")

init_db()
