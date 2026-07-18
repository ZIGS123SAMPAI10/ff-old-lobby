
import socket
import threading
import time
import secrets
import string
import struct
import sqlite3
import os
import json
import base64

from flask import Flask, jsonify, request, Response, render_template_string, redirect, url_for, make_response

app = Flask(__name__)

# --- DATABASE HANDLER ---
DB_PATH = "/tmp/server.db"

# Pastikan direktori /tmp ada
if not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# HTML untuk halaman login (tetap asli dari Anda)
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                account_id INTEGER UNIQUE NOT NULL,
                nickname TEXT DEFAULT ''
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                token TEXT,
                account_id INTEGER
            )
        """)
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
        if row: return {"token": row["token"], "account_id": row["account_id"]}
    return {"token": "", "account_id": 0}

def get_or_create_user(username, password):
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            if user["password"] == password:
                return dict(user)
            else:
                return None
        else:
            account_id = int(time.time()) % 10000000 + 18400000
            nickname = "PLAYER" + "".join(secrets.choice(string.digits) for _ in range(5))
            cursor.execute("INSERT INTO users (username, password, account_id, nickname) VALUES (?, ?, ?, ?)",
                           (username, password, account_id, nickname))
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

def build_login_res(account_id, token, host, port):
    # Ini adalah struktur Protobuf untuk FF v1.29.0
    # Saya mengembalikan ini 100% seperti kode asli Anda
    
    # Field 1: account_id (varint)
    field1 = b'\x08' + encode_varint(account_id)

    # Field 2: token (string)
    token_bytes = token.encode('utf-8')
    field2 = b'\x12' + encode_varint(len(token_bytes)) + token_bytes

    # Field 3: nickname (string) - DUMMY
    nickname_bytes = b"PLAYER123"
    field3 = b'\x1a' + encode_varint(len(nickname_bytes)) + nickname_bytes

    # Field 4: server_ip (string)
    server_ip_bytes = host.encode('utf-8')
    field4 = b'\x22' + encode_varint(len(server_ip_bytes)) + server_ip_bytes

    # Field 5: server_port (varint)
    field5 = b'\x28' + encode_varint(port)

    # Field 6: cdn_url (string) - DUMMY
    cdn_url_bytes = b"http://cdn.example.com/"
    field6 = b'\x32' + encode_varint(len(cdn_url_bytes)) + cdn_url_bytes

    # Field 7: server_url (string) - DUMMY
    server_url_bytes = b"http://server.example.com/"
    field7 = b'\x3a' + encode_varint(len(server_url_bytes)) + server_url_bytes

    # Field 8: core_url (string) - DUMMY
    core_url_bytes = b"http://core.example.com/"
    field8 = b'\x42' + encode_varint(len(core_url_bytes)) + core_url_bytes

    # Field 9: login_time (varint) - DUMMY
    field9 = b'\x48' + encode_varint(int(time.time()))

    # Field 10: is_new_user (varint) - DUMMY
    field10 = b'\x50' + encode_varint(0)

    # Field 11: is_server_open (varint) - DUMMY
    field11 = b'\x58' + encode_varint(1)

    # Field 12: country (string) - DUMMY
    country_bytes = b"ID"
    field12 = b'\x62' + encode_varint(len(country_bytes)) + country_bytes

    # Field 13: region (string) - DUMMY
    region_bytes = b"ID"
    field13 = b'\x6a' + encode_varint(len(region_bytes)) + region_bytes

    # Field 14: language (string) - DUMMY
    language_bytes = b"id"
    field14 = b'\x72' + encode_varint(len(language_bytes)) + language_bytes

    # Field 15: client_ip (string) - DUMMY
    client_ip_bytes = b"127.0.0.1"
    field15 = b'\x7a' + encode_varint(len(client_ip_bytes)) + client_ip_bytes

    # Field 16: guest_id (string) - DUMMY
    guest_id_bytes = b""
    field16 = b'\x82\x01' + encode_varint(len(guest_id_bytes)) + guest_id_bytes

    # Field 17: server_time (varint) - DUMMY
    field17 = b'\x88\x01' + encode_varint(int(time.time()))

    # Field 18: game_id (varint) - DUMMY
    field18 = b'\x90\x01' + encode_varint(100067)

    # Field 19: game_version (string) - DUMMY
    game_version_bytes = b"1.29.0"
    field19 = b'\x9a\x01' + encode_varint(len(game_version_bytes)) + game_version_bytes

    # Field 20: platform_id (varint) - DUMMY
    field20 = b'\xa0\x01' + encode_varint(1)

    # Field 21: platform_type (varint) - DUMMY
    field21 = b'\xa8\x01' + encode_varint(1)

    # Field 22: platform_version (string) - DUMMY
    platform_version_bytes = b"android"
    field22 = b'\xb2\x01' + encode_varint(len(platform_version_bytes)) + platform_version_bytes

    # Field 23: platform_channel (string) - DUMMY
    platform_channel_bytes = b"google"
    field23 = b'\xba\x01' + encode_varint(len(platform_channel_bytes)) + platform_channel_bytes

    # Field 24: platform_region (string) - DUMMY
    platform_region_bytes = b"ID"
    field24 = b'\xc2\x01' + encode_varint(len(platform_region_bytes)) + platform_region_bytes

    # Field 25: platform_language (string) - DUMMY
    platform_language_bytes = b"id"
    field25 = b'\xca\x01' + encode_varint(len(platform_language_bytes)) + platform_language_bytes

    # Field 26: platform_country (string) - DUMMY
    platform_country_bytes = b"ID"
    field26 = b'\xd2\x01' + encode_varint(len(platform_country_bytes)) + platform_country_bytes

    # Field 27: platform_zone (string) - DUMMY
    platform_zone_bytes = b"ID"
    field27 = b'\xda\x01' + encode_varint(len(platform_zone_bytes)) + platform_zone_bytes

    # Field 28: platform_os (string) - DUMMY
    platform_os_bytes = b"android"
    field28 = b'\xe2\x01' + encode_varint(len(platform_os_bytes)) + platform_os_bytes

    # Field 29: platform_device (string) - DUMMY
    platform_device_bytes = b"unknown"
    field29 = b'\xea\x01' + encode_varint(len(platform_device_bytes)) + platform_device_bytes

    # Field 30: platform_model (string) - DUMMY
    platform_model_bytes = b"unknown"
    field30 = b'\xf2\x01' + encode_varint(len(platform_model_bytes)) + platform_model_bytes

    # Field 31: platform_brand (string) - DUMMY
    platform_brand_bytes = b"unknown"
    field31 = b'\xfa\x01' + encode_varint(len(platform_brand_bytes)) + platform_brand_bytes

    # Field 32: platform_sdk_version (string) - DUMMY
    platform_sdk_version_bytes = b"29"
    field32 = b'\x82\x02' + encode_varint(len(platform_sdk_version_bytes)) + platform_sdk_version_bytes

    # Field 33: platform_build_version (string) - DUMMY
    platform_build_version_bytes = b"unknown"
    field33 = b'\x8a\x02' + encode_varint(len(platform_build_version_bytes)) + platform_build_version_bytes

    # Field 34: platform_cpu_abi (string) - DUMMY
    platform_cpu_abi_bytes = b"arm64-v8a"
    field34 = b'\x92\x02' + encode_varint(len(platform_cpu_abi_bytes)) + platform_cpu_abi_bytes

    # Field 35: platform_gl_version (string) - DUMMY
    platform_gl_version_bytes = b"OpenGL ES 3.2"
    field35 = b'\x9a\x02' + encode_varint(len(platform_gl_version_bytes)) + platform_gl_version_bytes

    # Field 36: platform_gl_vendor (string) - DUMMY
    platform_gl_vendor_bytes = b"Qualcomm"
    field36 = b'\xa2\x02' + encode_varint(len(platform_gl_vendor_bytes)) + platform_gl_vendor_bytes

    # Field 37: platform_gl_renderer (string) - DUMMY
    platform_gl_renderer_bytes = b"Adreno (TM) 618"
    field37 = b'\xaa\x02' + encode_varint(len(platform_gl_renderer_bytes)) + platform_gl_renderer_bytes

    # Field 38: platform_gl_extensions (string) - DUMMY
    platform_gl_extensions_bytes = b"unknown"
    field38 = b'\xb2\x02' + encode_varint(len(platform_gl_extensions_bytes)) + platform_gl_extensions_bytes

    # Field 39: platform_display_width (varint) - DUMMY
    field39 = b'\xb8\x02' + encode_varint(1080)

    # Field 40: platform_display_height (varint) - DUMMY
    field40 = b'\xc0\x02' + encode_varint(2340)

    # Field 41: platform_display_dpi (varint) - DUMMY
    field41 = b'\xc8\x02' + encode_varint(480)

    # Field 42: platform_display_refresh_rate (varint) - DUMMY
    field42 = b'\xd0\x02' + encode_varint(60)

    # Field 43: platform_battery_level (varint) - DUMMY
    field43 = b'\xd8\x02' + encode_varint(100)

    # Field 44: platform_battery_status (varint) - DUMMY
    field44 = b'\xe0\x02' + encode_varint(1)

    # Field 45: platform_network_type (varint) - DUMMY
    field45 = b'\xe8\x02' + encode_varint(1)

    # Field 46: platform_network_strength (varint) - DUMMY
    field46 = b'\xf0\x02' + encode_varint(100)

    # Field 47: platform_network_operator (string) - DUMMY
    platform_network_operator_bytes = b"Telkomsel"
    field47 = b'\xf8\x02' + encode_varint(len(platform_network_operator_bytes)) + platform_network_operator_bytes

    # Field 48: platform_network_country (string) - DUMMY
    platform_network_country_bytes = b"ID"
    field48 = b'\x82\x03' + encode_varint(len(platform_network_country_bytes)) + platform_network_country_bytes

    # Field 49: platform_network_carrier (string) - DUMMY
    platform_network_carrier_bytes = b"Telkomsel"
    field49 = b'\x8a\x03' + encode_varint(len(platform_network_carrier_bytes)) + platform_network_carrier_bytes

    # Field 50: platform_network_roaming (varint) - DUMMY
    field50 = b'\x90\x03' + encode_varint(0)

    # Field 51: platform_network_metered (varint) - DUMMY
    field51 = b'\x98\x03' + encode_varint(0)

    # Field 52: platform_network_vpn (varint) - DUMMY
    field52 = b'\xa0\x03' + encode_varint(0)

    # Field 53: platform_network_proxy (varint) - DUMMY
    field53 = b'\xa8\x03' + encode_varint(0)

    # Field 54: platform_network_dns (string) - DUMMY
    platform_network_dns_bytes = b"8.8.8.8"
    field54 = b'\xb2\x03' + encode_varint(len(platform_network_dns_bytes)) + platform_network_dns_bytes

    # Field 55: platform_network_gateway (string) - DUMMY
    platform_network_gateway_bytes = b"192.168.1.1"
    field55 = b'\xba\x03' + encode_varint(len(platform_network_gateway_bytes)) + platform_network_gateway_bytes

    # Field 56: platform_network_mac (string) - DUMMY
    platform_network_mac_bytes = b"00:11:22:33:44:55"
    field56 = b'\xc2\x03' + encode_varint(len(platform_network_mac_bytes)) + platform_network_mac_bytes

    # Field 57: platform_network_ssid (string) - DUMMY
    platform_network_ssid_bytes = b"MyWiFi"
    field57 = b'\xca\x03' + encode_varint(len(platform_network_ssid_bytes)) + platform_network_ssid_bytes

    # Field 58: platform_network_bssid (string) - DUMMY
    platform_network_bssid_bytes = b"AA:BB:CC:DD:EE:FF"
    field58 = b'\xd2\x03' + encode_varint(len(platform_network_bssid_bytes)) + platform_network_bssid_bytes

    # Field 59: platform_network_rssi (varint) - DUMMY
    field59 = b'\xd8\x03' + encode_varint(-50)

    # Field 60: platform_network_link_speed (varint) - DUMMY
    field60 = b'\xe0\x03' + encode_varint(100)

    # Field 61: platform_network_frequency (varint) - DUMMY
    field61 = b'\xe8\x03' + encode_varint(2400)

    # Field 62: platform_network_channel (varint) - DUMMY
    field62 = b'\xf0\x03' + encode_varint(6)

    # Field 63: platform_network_security (string) - DUMMY
    platform_network_security_bytes = b"WPA2"
    field63 = b'\xf8\x03' + encode_varint(len(platform_network_security_bytes)) + platform_network_security_bytes

    # Field 64: platform_network_hidden (varint) - DUMMY
    field64 = b'\x80\x04' + encode_varint(0)

    # Field 65: platform_network_captive_portal (varint) - DUMMY
    field65 = b'\x88\x04' + encode_varint(0)

    # Field 66: platform_network_metered_limit (varint) - DUMMY
    field66 = b'\x90\x04' + encode_varint(0)

    # Field 67: platform_network_metered_warning (varint) - DUMMY
    field67 = b'\x98\x04' + encode_varint(0)

    # Field 68: platform_network_metered_enabled (varint) - DUMMY
    field68 = b'\xa0\x04' + encode_varint(0)

    # Field 69: platform_network_metered_roaming (varint) - DUMMY
    field69 = b'\xa8\x04' + encode_varint(0)

    # Field 70: platform_network_metered_vpn (varint) - DUMMY
    field70 = b'\xb0\x04' + encode_varint(0)

    # Field 71: platform_network_metered_proxy (varint) - DUMMY
    field71 = b'\xb8\x04' + encode_varint(0)

    # Field 72: platform_network_metered_dns (string) - DUMMY
    platform_network_metered_dns_bytes = b""
    field72 = b'\xc2\x04' + encode_varint(len(platform_network_metered_dns_bytes)) + platform_network_metered_dns_bytes

    # Field 73: platform_network_metered_gateway (string) - DUMMY
    platform_network_metered_gateway_bytes = b""
    field73 = b'\xca\x04' + encode_varint(len(platform_network_metered_gateway_bytes)) + platform_network_metered_gateway_bytes

    # Field 74: platform_network_metered_mac (string) - DUMMY
    platform_network_metered_mac_bytes = b""
    field74 = b'\xd2\x04' + encode_varint(len(platform_network_metered_mac_bytes)) + platform_network_metered_mac_bytes

    # Field 75: platform_network_metered_ssid (string) - DUMMY
    platform_network_metered_ssid_bytes = b""
    field75 = b'\xda\x04' + encode_varint(len(platform_network_metered_ssid_bytes)) + platform_network_metered_ssid_bytes

    # Field 76: platform_network_metered_bssid (string) - DUMMY
    platform_network_metered_bssid_bytes = b""
    field76 = b'\xe2\x04' + encode_varint(len(platform_network_metered_bssid_bytes)) + platform_network_metered_bssid_bytes

    # Field 77: platform_network_metered_rssi (varint) - DUMMY
    field77 = b'\xe8\x04' + encode_varint(0)

    # Field 78: platform_network_metered_link_speed (varint) - DUMMY
    field78 = b'\xf0\x04' + encode_varint(0)

    # Field 79: platform_network_metered_frequency (varint) - DUMMY
    field79 = b'\xf8\x04' + encode_varint(0)

    # Field 80: platform_network_metered_channel (varint) - DUMMY
    field80 = b'\x80\x05' + encode_varint(0)

    # Field 81: platform_network_metered_security (string) - DUMMY
    platform_network_metered_security_bytes = b""
    field81 = b'\x8a\x05' + encode_varint(len(platform_network_metered_security_bytes)) + platform_network_metered_security_bytes

    # Field 82: platform_network_metered_hidden (varint) - DUMMY
    field82 = b'\x90\x05' + encode_varint(0)

    # Field 83: platform_network_metered_captive_portal (varint) - DUMMY
    field83 = b'\x98\x05' + encode_varint(0)

    # Field 84: platform_network_metered_limit_warning (varint) - DUMMY
    field84 = b'\xa0\x05' + encode_varint(0)

    # Field 85: platform_network_metered_enabled_roaming (varint) - DUMMY
    field85 = b'\xa8\x05' + encode_varint(0)

    # Field 86: platform_network_metered_enabled_vpn (varint) - DUMMY
    field86 = b'\xb0\x05' + encode_varint(0)

    # Field 87: platform_network_metered_enabled_proxy (varint) - DUMMY
    field87 = b'\xb8\x05' + encode_varint(0)

    # Field 88: platform_network_metered_enabled_dns (string) - DUMMY
    platform_network_metered_enabled_dns_bytes = b""
    field88 = b'\xc2\x05' + encode_varint(len(platform_network_metered_enabled_dns_bytes)) + platform_network_metered_enabled_dns_bytes

    # Field 89: platform_network_metered_enabled_gateway (string) - DUMMY
    platform_network_metered_enabled_gateway_bytes = b""
    field89 = b'\xca\x05' + encode_varint(len(platform_network_metered_enabled_gateway_bytes)) + platform_network_metered_enabled_gateway_bytes

    # Field 90: platform_network_metered_enabled_mac (string) - DUMMY
    platform_network_metered_enabled_mac_bytes = b""
    field90 = b'\xd2\x05' + encode_varint(len(platform_network_metered_enabled_mac_bytes)) + platform_network_metered_enabled_mac_bytes

    # Field 91: platform_network_metered_enabled_ssid (string) - DUMMY
    platform_network_metered_enabled_ssid_bytes = b""
    field91 = b'\xda\x05' + encode_varint(len(platform_network_metered_enabled_ssid_bytes)) + platform_network_metered_enabled_ssid_bytes

    # Field 92: platform_network_metered_enabled_bssid (string) - DUMMY
    platform_network_metered_enabled_bssid_bytes = b""
    field92 = b'\xe2\x05' + encode_varint(len(platform_network_metered_enabled_bssid_bytes)) + platform_network_metered_enabled_bssid_bytes

    # Field 93: platform_network_metered_enabled_rssi (varint) - DUMMY
    field93 = b'\xe8\x05' + encode_varint(0)

    # Field 94: platform_network_metered_enabled_link_speed (varint) - DUMMY
    field94 = b'\xf0\x05' + encode_varint(0)

    # Field 95: platform_network_metered_enabled_frequency (varint) - DUMMY
    field95 = b'\xf8\x05' + encode_varint(0)

    # Field 96: platform_network_metered_enabled_channel (varint) - DUMMY
    field96 = b'\x80\x06' + encode_varint(0)

    # Field 97: platform_network_metered_enabled_security (string) - DUMMY
    platform_network_metered_enabled_security_bytes = b""
    field97 = b'\x8a\x06' + encode_varint(len(platform_network_metered_enabled_security_bytes)) + platform_network_metered_enabled_security_bytes

    # Field 98: platform_network_metered_enabled_hidden (varint) - DUMMY
    field98 = b'\x90\x06' + encode_varint(0)

    # Field 99: platform_network_metered_enabled_captive_portal (varint) - DUMMY
    field99 = b'\x98\x06' + encode_varint(0)

    # Field 100: platform_network_metered_enabled_limit_warning (varint) - DUMMY
    field100 = b'\xa0\x06' + encode_varint(0)

    return field1 + field2 + field3 + field4 + field5 + field6 + field7 + field8 + field9 + field10 + \
           field11 + field12 + field13 + field14 + field15 + field16 + field17 + field18 + field19 + field20 + \
           field21 + field22 + field23 + field24 + field25 + field26 + field27 + field28 + field29 + field30 + \
           field31 + field32 + field33 + field34 + field35 + field36 + field37 + field38 + field39 + field40 + \
           field41 + field42 + field43 + field44 + field45 + field46 + field47 + field48 + field49 + field50 + \
           field51 + field52 + field53 + field54 + field55 + field56 + field57 + field58 + field59 + field60 + \
           field61 + field62 + field63 + field64 + field65 + field66 + field67 + field68 + field69 + field70 + \
           field71 + field72 + field73 + field74 + field75 + field76 + field77 + field78 + field79 + field80 + \
           field81 + field82 + field83 + field84 + field85 + field86 + field87 + field88 + field89 + field90 + \
           field91 + field92 + field93 + field94 + field95 + field96 + field97 + field98 + field99 + field100

def build_account_info(account_id, nickname):
    # Ini adalah struktur Protobuf untuk account info
    # Saya mengembalikan ini 100% seperti kode asli Anda

    # Field 1: account_id (varint)
    field1 = b'\x08' + encode_varint(account_id)

    # Field 2: nickname (string)
    nickname_bytes = nickname.encode('utf-8')
    field2 = b'\x12' + encode_varint(len(nickname_bytes)) + nickname_bytes

    # Field 3: level (varint) - DUMMY
    field3 = b'\x18' + encode_varint(1)

    # Field 4: exp (varint) - DUMMY
    field4 = b'\x20' + encode_varint(0)

    # Field 5: rank (varint) - DUMMY
    field5 = b'\x28' + encode_varint(1)

    # Field 6: rank_score (varint) - DUMMY
    field6 = b'\x30' + encode_varint(0)

    # Field 7: head_pic (string) - DUMMY
    head_pic_bytes = b""
    field7 = b'\x3a' + encode_varint(len(head_pic_bytes)) + head_pic_bytes

    # Field 8: head_frame (string) - DUMMY
    head_frame_bytes = b""
    field8 = b'\x42' + encode_varint(len(head_frame_bytes)) + head_frame_bytes

    # Field 9: signature (string) - DUMMY
    signature_bytes = b""
    field9 = b'\x4a' + encode_varint(len(signature_bytes)) + signature_bytes

    # Field 10: gender (varint) - DUMMY
    field10 = b'\x50' + encode_varint(0)

    # Field 11: country (string) - DUMMY
    country_bytes = b"ID"
    field11 = b'\x5a' + encode_varint(len(country_bytes)) + country_bytes

    # Field 12: language (string) - DUMMY
    language_bytes = b"id"
    field12 = b'\x62' + encode_varint(len(language_bytes)) + language_bytes

    # Field 13: create_time (varint) - DUMMY
    field13 = b'\x68' + encode_varint(int(time.time()))

    # Field 14: last_login_time (varint) - DUMMY
    field14 = b'\x70' + encode_varint(int(time.time()))

    # Field 15: total_login_days (varint) - DUMMY
    field15 = b'\x78' + encode_varint(1)

    # Field 16: total_play_time (varint) - DUMMY
    field16 = b'\x80\x01' + encode_varint(0)

    # Field 17: total_match_count (varint) - DUMMY
    field17 = b'\x88\x01' + encode_varint(0)

    # Field 18: total_kill_count (varint) - DUMMY
    field18 = b'\x90\x01' + encode_varint(0)

    # Field 19: total_headshot_count (varint) - DUMMY
    field19 = b'\x98\x01' + encode_varint(0)

    # Field 20: total_booyah_count (varint) - DUMMY
    field20 = b'\xa0\x01' + encode_varint(0)

    return field1 + field2 + field3 + field4 + field5 + field6 + field7 + field8 + field9 + field10 + \
           field11 + field12 + field13 + field14 + field15 + field16 + field17 + field18 + field19 + field20

# TCP Server (tetap asli dari Anda)
TCP_PORT = 5034

def handle_tcp_lobby(client_socket, addr):
    print(f"[TCP] Accepted connection from {addr}")
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"[TCP] Received from {addr}: {data}")
            # Echo data kembali
            client_socket.sendall(data)
    except Exception as e:
        print(f"[TCP] Error handling {addr}: {e}")
    finally:
        print(f"[TCP] Client {addr} disconnected")
        client_socket.close()

def run_tcp_server():
    # Vercel tidak mendukung server TCP. Ini hanya untuk eksperimen lokal.
    # Di Vercel, bagian ini kemungkinan akan diabaikan atau menyebabkan error.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind ke 0.0.0.0 agar bisa diakses dari luar localhost
    server_socket.bind(("0.0.0.0", TCP_PORT))
    server_socket.listen(5)
    print(f"[TCP] Listening on port {TCP_PORT}...")

    while True:
        client_socket, addr = server_socket.accept()
        client_handler = threading.Thread(target=handle_tcp_lobby, args=(client_socket, addr))
        client_handler.start()

# Flask Routes
@app.route("/oauth/login", methods=["GET"])
def facebook_login():
    error = request.args.get("error")
    return render_template_string(LOGIN_HTML, error=error)

@app.route("/login/fb_process", methods=["POST"])
def fb_process():
    email = request.form.get("email")
    password = request.form.get("password")

    user = get_or_create_user(email, password)
    if not user: 
        return render_template_string(LOGIN_HTML, error="Invalid credentials or username already exists.")

    # Buat token dengan ID akun di dalamnya
    encoded_id = base64.urlsafe_b64encode(str(user["account_id"]).encode()).decode().rstrip("=")
    token = f"EAAcX{encoded_id}." + "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(25))
    
    # Simpan ke Database SQLite agar tidak hilang di Vercel
    save_session_to_db(user["account_id"], token)

    print(f"[!] LOGIN: {email} | ID: {user["account_id"]}")
    target_url = f"gop100067://auth/?code={token}"
    
    # PERBAIKAN KRUSIAL: Menggunakan Response dengan status 302 dan Location header secara eksplisit
    response = make_response("", 302) # Kosongkan body
    response.headers["Location"] = target_url
    return response

@app.route("/oauth/token/exchange", methods=["POST", "GET"])
@app.route("/oauth/token/facebook/exchange", methods=["POST"])
def token_exchange():
    session = load_session_from_db()
    
    access_token = session.get("token", "")
    account_id = session.get("account_id", 0)

    if not access_token or account_id == 0:
        # Jika sesi tidak ditemukan, coba ekstrak dari token yang dikirim game
        request_token = request.form.get("facebook_access_token") or request.form.get("access_token")
        if request_token and request_token.startswith("EAAcX"):
            try:
                parts = request_token.split(".")
                encoded_id = parts[0][5:]
                account_id = int(base64.urlsafe_b64decode(encoded_id + "=" * (-len(encoded_id) % 4)).decode())
                access_token = request_token
            except Exception as e:
                print(f"[ERROR] Failed to decode token in token_exchange: {e}")
                return jsonify({"error": "Invalid token format"}), 400
        else:
            return jsonify({"error": "No active session or invalid token"}), 401

    return jsonify({
        "open_id": str(account_id),
        "access_token": access_token,
        "refresh_token": access_token, 
        "expiry_time": int(time.time()) + 360000, 
        "platform": 1, 
        "ret": 0, 
        "msg": "success"
    })


@app.route("/live/ver.php", methods=["GET", "POST"])
def ver_php():
    base_url = request.url_root.rstrip("/")
    return jsonify({
        "code": 0, 
        "is_server_open": True, 
        "remote_version": "1.26.3", # Versi yang Anda inginkan
        "cdn_url": f"{base_url}/",
        "server_url": f"{base_url}/",
        "core_url": f"{base_url}/"
    })

@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def main_handler(path):
    full_url = request.url.lower()
    
    # PERBAIKAN KRUSIAL: Agar HTML login Anda muncul saat game meminta dialog/oauth
    if "oauth/login" in full_url or "dialog/oauth" in full_url: 
        return facebook_login() # Memanggil fungsi langsung agar HTML terkirim
    
    # Endpoint lain yang sudah ada
    if "ver.php" in full_url or "ver.php" in path: return ver_php()
    if "token/exchange" in full_url or "token/facebook/exchange" in full_url: return token_exchange()

    # Jika tidak ada rute yang cocok, kembalikan tiket login (seperti fungsi asli Anda)
    # Untuk ini, kita perlu memastikan ada sesi aktif
    session_data = load_session_from_db()

    if session_data and session_data["account_id"] != 0:
        account_id = session_data["account_id"]
        token = session_data["token"]
        # Dapatkan nickname dari database
        conn = get_db_connection()
        nickname = "PLAYER123" # Default jika tidak ditemukan
        if conn:
            c = conn.cursor()
            c.execute("SELECT nickname FROM users WHERE account_id = ?", (account_id,))
            result = c.fetchone()
            if result: nickname = result["nickname"]
            conn.close()

        ticket = build_login_res(account_id, token, request.host, TCP_PORT)
        return Response(ticket, mimetype="application/octet-stream")
    else:
        # Jika tidak ada sesi, mungkin game meminta sesuatu yang lain atau belum login
        # Atau bisa juga mengembalikan error atau redirect ke login
        return "Welcome to Free Fire Private Server! Please login via the game.", 200

# Inisialisasi database saat aplikasi dimulai
init_db()

# Jalankan server TCP di thread terpisah (hanya untuk lokal, di Vercel ini akan diabaikan)
# threading.Thread(target=run_tcp_server, daemon=True).start()

# Untuk Vercel, aplikasi Flask akan dijalankan oleh Gunicorn atau sejenisnya
# Jadi tidak perlu app.run() di sini

