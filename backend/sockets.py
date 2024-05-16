import socketio

socketio_server = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[]
)

socketio_app = socketio.ASGIApp(
    socketio_server=socketio_server,
    socketio_path='sockets'
)


@socketio_server.event
async def connect(sid, environ, auth):
    print(f'{sid}: connected')
    await socketio_server.emit('join', {'sid': sid})


@socketio_server.event
async def chat(sid, message):
    await socketio_server.emit('chat', {'sid': sid, 'message': message})


@socketio_server.event
async def disconnect(sid):
    print(f'{sid}: disconnected')