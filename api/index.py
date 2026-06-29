from flask import Flask, request, Response
import api.MajorLogin_pb2 as MajorLogin_pb2

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST']) # Jalur utama (/) agar pendek
def lobby():
    if request.method == 'GET':
        return "Server Online! 🗿"
    
    try:
        raw_data = request.get_data()
        ff_req = MajorLogin_pb2.request()
        ff_req.ParseFromString(raw_data)
        
        ff_res = MajorLogin_pb2.response()
        ff_res.accountId = ff_req.accountid
        ff_res.lockRegion = "ID"
        ff_res.token = "SESSION_26_CHAR"
        ff_res.serverUrl = request.url_root
        
        return Response(ff_res.SerializeToString(), mimetype='application/x-protobuf')
    except:
        return "Error", 500

app = app
