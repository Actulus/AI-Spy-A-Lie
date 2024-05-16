import os
from flask import request, jsonify
from flask_socketio import SocketIO, emit

# App Initialization
from . import create_app  # from __init__ file

app = create_app(os.getenv("CONFIG_MODE"))
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({"msg": "Hello from Flask!"})


@app.route("/http-call")
def http_call():
    """return JSON with string data as the value"""
    data = {"data": "This text was fetched using an HTTP call to server on render"}
    return jsonify(data)


@socketio.on("connect")
def connected():
    """event listener when client connects to the server"""
    print(request.sid)
    print("client has connected")
    emit("connect", {"data": f"id: {request.sid} is connected"})


@socketio.on("data")
def handle_message(data):
    """event listener when client types a message"""
    print("data from the front end: ", str(data))
    emit("data", {"data": data, "id": request.sid}, broadcast=True)


@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the server"""
    print("user disconnected")
    emit("disconnect", f"user {request.sid} disconnected", broadcast=True)


if __name__ == "__main__":
    # app.run()
    socketio.run(app, debug=True, log_output=True)  # run the app with socketio
