import random
import socketio
import uuid
import logging
import asyncio
from liars_dice_game_logic import LiarDiceGame

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

socketio_server = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[]
)

socketio_app = socketio.ASGIApp(
    socketio_server=socketio_server,
    socketio_path='/'
)

rooms = {}  # Dictionary to keep track of rooms and their connections
games = {}  # Dictionary to keep track of games and their states

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
    games[room] = LiarDiceGame()

    await socketio_server.enter_room(sid, room)
    logger.info(f'{sid}: connected to {room}')
    await socketio_server.emit('join', {'sid': sid}, room=room)
    
    # Emit the initial game state to the user
    game_state = games[room].get_game_state()
    await socketio_server.emit('game_update', game_state, room=room)

    # Simulate AI connection
    asyncio.create_task(simulate_ai_connection(room))

@socketio_server.event
async def player_names(sid, data):
    room = None
    for r, sids in rooms.items():
        if sid in sids:
            room = r
            break
    
    if room:
        user_name = data['userName']
        ai_name = data['aiName']
        games[room].set_player_names(user_name, ai_name)
        logger.info(f'Player names received in {room}: {user_name}, {ai_name}')
        # Update game state with player names
        game_state = games[room].get_game_state()
        await socketio_server.emit('game_update', game_state, room=room)

@socketio_server.event
async def chat(sid, message):
    room = None
    for r, sids in rooms.items():
        if sid in sids:
            room = r
            break

    if room:
        logger.info(f'Message from {sid} in {room}: {message}')
        game = games[room]
        response_message = None
        user_message = None
        # await socketio_server.emit('chat', {'sid': sid, 'message': message}, room=room)
        
        # If the message is from the user, let the AI respond
        if not sid.startswith('ai_'):
            # handle player move
            if message.startswith('bid'):
                _, quantity, face_value = message.split()
                quantity = int(quantity)
                face_value = int(face_value)
                success = game.make_bid(1, quantity, face_value)  # Assuming player 1 is the user
                
                if success:
                    user_message = f"Bid: {quantity} {face_value}s."
                    response_message = "Bid successful."
                else:
                    user_message = "Invalid bid."
                    response_message = "Invalid bid."
                
                # await socketio_server.emit('chat', {'sid': sid, 'message': response_message}, room=room)
            elif message == "challenge":
                result = game.challenge(1)
                user_message = "Challenge!"
                response_message = result

                # await socketio_server.emit('chat', {'sid': sid, 'message': result}, room=room)

            # Send the user message only to the user
            if user_message:
                await socketio_server.emit('chat', {'sid': sid, 'message': user_message}, room=sid)
                if message == "challenge":
                    await asyncio.sleep(0.5)
                    await socketio_server.emit('chat', {'sid': sid, 'message': response_message}, room=room)

            
            # Send game state update to all users
            game_state = game.get_game_state()
            await socketio_server.emit('game_update', game_state, room=room)

            # AI response based on the game state
            if game.is_game_over():
                winner = game.get_winner()
                await socketio_server.emit('game_over', {'winner': game.player_names[winner]}, room=room)
            else:
                ai_sid = f'ai_{room}'
                if game.is_game_over():
                    winner = game.get_winner()
                    await socketio_server.emit('chat', {'sid': ai_sid, 'message': f"Game over! Player {winner} wins!"}, room=room)
                else:
                    await asyncio.sleep(0.5)  # Adding delay before AI response
                    ai_message = generate_ai_response(game, room)
                    await socketio_server.emit('chat', {'sid': ai_sid, 'message': ai_message}, room=room)
                    # Send updated game state after AI move
                    game_state = game.get_game_state()
                    await socketio_server.emit('game_update', game_state, room=room)

@socketio_server.event
async def disconnect(sid):
    room = None
    for r, sids in rooms.items():
        if sid in sids:
            sids.remove(sid)
            room = r
            if not sids:  # If the room is empty, remove it from the dictionary
                del rooms[room]
                del games[room]
            break

    if room:
        logger.info(f'{sid}: disconnected from {room}')

async def simulate_ai_connection(room):
    ai_sid = f'ai_{room}'
    rooms[room].add(ai_sid)
    logger.info(f'AI {ai_sid}: connected to {room}')
    await socketio_server.emit('join', {'sid': ai_sid}, room=room)
    await socketio_server.emit('chat', {'sid': ai_sid, 'message': 'Hi there!'}, room=room)

def generate_ai_response(game, room):
    if game.is_game_over():
        winner = game.get_winner()
        return f"Game over! {game.player_names[winner]} wins!"
    
    if game.last_action_was_challenge or game.current_bid == (1, 1):
        action = 'bid'  # Force bid after challenge or for the first move
    else:
        action = random.choice(['bid', 'challenge'])

    # if current bid is 10 6s, challenge
    if game.current_bid[0] == 10:
        action = 'challenge'

    if action == 'bid':
        quantity, face_value = game.random_bid()
        game.make_bid(2, quantity, face_value)  # Assuming player 2 is the AI
        return f"Bid: {quantity} {face_value}s."
    else:
        result = game.challenge(2)
        return f"Challenge! {result}"
