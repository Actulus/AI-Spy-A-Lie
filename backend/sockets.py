import socketio
import subprocess
import os
import uuid

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
async def connect(sid, environ):
    query_params = environ.get('QUERY_STRING', '')
    room = ''
    if query_params:
        params = dict(qc.split('=') for qc in query_params.split('&'))
        difficulty = params.get('room', 'default_room')
        room = f'{difficulty}_{uuid.uuid4()}'
    else:
        room = f'default_room_{uuid.uuid4()}'

    rooms[room] = {sid}

    await socketio_server.enter_room(sid, room)
    print(f'{sid}: connected to {room}')
    await socketio_server.emit('join', {'sid': sid}, room=room)
    
    await connect_ai_to_room(room)

@socketio_server.event
async def chat(sid, message):
    room = None
    for r, sids in rooms.items():
        if sid in sids:
            room = r
            break

    if room:
        await socketio_server.emit('chat', {'sid': sid, 'message': message}, room=room)

@socketio_server.event
async def disconnect(sid):
    room = None
    for r, sids in rooms.items():
        if sid in sids:
            sids.remove(sid)
            room = r
            if not sids:  # If the room is empty, remove it from the dictionary
                del rooms[room]
            break

    if room:
        print(f'{sid}: disconnected from {room}')

async def connect_ai_to_room(room):
    ai_sid = f'ai_{room}'
    rooms[room].add(ai_sid)
    # Correctly register the AI room in the manager
    socketio_server.manager.enter_room(ai_sid, '/', room)
    await socketio_server.emit('join', {'sid': ai_sid}, room=room)
    await socketio_server.emit('chat', {'sid': ai_sid, 'message': 'Hello! I am the AI.'}, room=room)
    
    # Call the AI client
    subprocess.Popen([os.sys.executable, 'client.py', room])
