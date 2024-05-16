import socketio

socketio_server = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[]
)

socketio_app = socketio.ASGIApp(
    socketio_server=socketio_server,
    socketio_path='sockets'
)

rooms = {}  # Dictionary to keep track of rooms and their connections

@socketio_server.event
async def connect(sid, environ, auth):
    room = 'default_room'  # Example room name; adjust as needed

    # Ensure the room exists in the dictionary
    if room not in rooms:
        rooms[room] = set()

    # Check the number of connections in the room
    if len(rooms[room]) < 2:
        rooms[room].add(sid)
        await socketio_server.enter_room(sid, room)
        print(f'{sid}: connected to {room}')
        await socketio_server.emit('join', {'sid': sid}, room=room)
    else:
        print(f'{sid}: connection rejected - room {room} full')
        await socketio_server.disconnect(sid)

@socketio_server.event
async def chat(sid, message):
    room = 'default_room'  # Example room name; adjust as needed
    await socketio_server.emit('chat', {'sid': sid, 'message': message}, room=room)

@socketio_server.event
async def disconnect(sid):
    room = 'default_room'  # Example room name; adjust as needed
    if room in rooms and sid in rooms[room]:
        rooms[room].remove(sid)
        if not rooms[room]:  # If the room is empty, remove it from the dictionary
            del rooms[room]
        print(f'{sid}: disconnected from {room}')
