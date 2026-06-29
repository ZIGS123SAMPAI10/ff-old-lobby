from flask import Flask, request, Response
import api.MajorLogin_pb2 as MajorLogin_pb2
import json

app = Flask(__name__)

@app.route('/')
def home():
    return "Lobby Server FF Old is Online! 🗿"

@app.route('/login', methods=['POST'])
def login():
    try:
        raw_data = request.get_data()
        ff_req = MajorLogin_pb2.request()
        ff_req.ParseFromString(raw_data)
        print(f"Login Request: {ff_req.nickname}")
        ff_res = MajorLogin_pb2.response()
        ff_res.accountId = ff_req.accountid
        ff_res.lockRegion = "ID"
        ff_res.token = "LOBBY_BY_MANUS_AI"
        ff_res.serverUrl = request.url_root
        return Response(ff_res.SerializeToString(), mimetype='application/x-protobuf')
    except Exception as e:
        return str(e), 500

app = app
