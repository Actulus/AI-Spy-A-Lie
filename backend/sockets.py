import socketio
import uuid
import logging
import asyncio

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

socketio_server = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[]
)

socketio_app = socketio.ASGIApp(
    socketio_server=socketio_server,
    socketio_path='sockets'
)

rooms = {}  # Dictionary to keep track of rooms and their connections

def generate_room_name(difficulty):
    return f'{difficulty}_{uuid.uuid4()}'

@socketio_server.event
async def connect(sid, environ):
    query_params = environ.get('QUERY_STRING', '')
    if query_params:
        params = dict(qc.split('=') for qc in query_params.split('&'))
        difficulty = params.get('room', 'default_room')
        room = generate_room_name(difficulty)
    else:
        room = generate_room_name('default_room')

    rooms[room] = {sid}

    await socketio_server.enter_room(sid, room)
    logger.info(f'{sid}: connected to {room}')
    await socketio_server.emit('join', {'sid': sid}, room=room)
    
    # Simulate AI connection
    asyncio.create_task(simulate_ai_connection(room))

@socketio_server.event
async def chat(sid, message):
    room = None
    for r, sids in rooms.items():
        if sid in sids:
            room = r
            break

    if room:
        logger.info(f'Message from {sid} in {room}: {message}')
        await socketio_server.emit('chat', {'sid': sid, 'message': message}, room=room)
        # If the message is from the user, let the AI respond
        if not sid.startswith('ai_'):
            ai_sid = f'ai_{room}'
            ai_message = generate_ai_response(message)
            await socketio_server.emit('chat', {'sid': ai_sid, 'message': ai_message}, room=room)

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
        logger.info(f'{sid}: disconnected from {room}')

async def simulate_ai_connection(room):
    ai_sid = f'ai_{room}'
    rooms[room].add(ai_sid)
    logger.info(f'AI {ai_sid}: connected to {room}')
    await socketio_server.emit('join', {'sid': ai_sid}, room=room)
    await socketio_server.emit('chat', {'sid': ai_sid, 'message': 'Hello! I am the AI.'}, room=room)

def generate_ai_response(message):
    # Simple echo response for demonstration
    return f"{message}"
