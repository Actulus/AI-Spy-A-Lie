import random
import socketio
import uuid
import logging
import asyncio
from liars_dice_game_logic import LiarDiceGame
import pickle
import torch
import sys
import os
from collections import deque
import numpy as np
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.cuda.amp import GradScaler, autocast

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define QLearningAgent, DQN, and DQNAgent classes
class QLearningAgent:
    def __init__(self, action_size, state_size, alpha=0.1, gamma=0.99, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        self.action_size = action_size
        self.state_size = state_size
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.q_table = {}

    def get_state_key(self, state):
        return str(state)

    def get_action(self, state):
        state_key = self.get_state_key(state)
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(range(self.action_size))
        if state_key not in self.q_table:
            return random.choice(range(self.action_size))
        return np.argmax(self.q_table[state_key])

# Define the correct state size based on the saved model
state_size = 12  # Adjusted to match the saved model

class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class DQNAgent:
    def __init__(self, state_size, action_size, gamma=0.99, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, lr=0.0001, batch_size=256, memory_size=100000):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=memory_size)
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.lr = lr
        self.batch_size = batch_size
        self.model = DQN(state_size, action_size).to(device)
        self.target_model = DQN(state_size, action_size).to(device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.update_target_model()

    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def flatten_state(self, state):
        # Ensure the state is flattened to the correct size
        dice_count = np.array(list(state['dice_count'].values()))
        current_bid = np.array(state['current_bid'])
        current_player = np.array([state['current_player']])
        last_action_was_challenge = np.array([state['last_action_was_challenge']])
        scores = np.array(list(state['scores'].values()))

        flattened_state = np.concatenate([
            dice_count,
            current_bid,
            current_player,
            last_action_was_challenge,
            scores
        ])

        # Add additional padding to match the required state size of 12 if necessary
        if flattened_state.size < state_size:
            flattened_state = np.pad(flattened_state, (0, state_size - flattened_state.size), 'constant')

        return flattened_state

    def get_action(self, state):
        state = self.flatten_state(state)
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        state = torch.FloatTensor(state).unsqueeze(0).to(device)
        with torch.no_grad():
            q_values = self.model(state)
        return q_values.argmax().item()


class BayesianAgent:
    def __init__(self, num_players, num_dice):
        self.num_players = num_players
        self.num_dice = num_dice
        self.beliefs = self.initialize_beliefs()

    def initialize_beliefs(self):
        beliefs = np.ones((self.num_players, 6)) / 6
        return beliefs

    def update_beliefs(self, state, action):
        if action['type'] == 'bid':
            bid_quantity, bid_face = action['quantity'], action['face']
            for player in range(self.num_players):
                if player != state['current_player']:
                    self.beliefs[player, bid_face - 1] *= bid_quantity / self.num_dice
                    self.beliefs[player] /= np.sum(self.beliefs[player])
        elif action['type'] == 'challenge':
            challenged_bid = state['current_bid']
            actual_quantity = state['dice_count'][challenged_bid[1] - 1]
            if actual_quantity >= challenged_bid[0]:
                for player in range(self.num_players):
                    if player != state['current_player']:
                        self.beliefs[player, challenged_bid[1] - 1] *= actual_quantity / self.num_dice
                        self.beliefs[player] /= np.sum(self.beliefs[player])
            else:
                for player in range(self.num_players):
                    if player != state['current_player']:
                        self.beliefs[player, challenged_bid[1] - 1] *= (self.num_dice - actual_quantity) / self.num_dice
                        self.beliefs[player] /= np.sum(self.beliefs[player])

    def get_action(self, state):
        total_dice = self.num_dice * self.num_players
        current_bid_face = state['current_bid'][1]
        
        # Ensure current_bid_face is valid and within bounds
        if current_bid_face - 1 < 0 or current_bid_face - 1 >= len(state['dice_count']):
            logging.error(f"Invalid current_bid_face: {current_bid_face}")
            return {'type': 'challenge'}

        remaining_dice = total_dice - state['dice_count'][current_bid_face - 1]
        prob_bid_correct = np.prod([np.sum(self.beliefs[player, current_bid_face - 1:]) for player in range(self.num_players) if player != state['current_player']])
        prob_bid_incorrect = 1 - prob_bid_correct

        if prob_bid_correct > 0.7:
            quantity = state['current_bid'][0] + 1
            face = current_bid_face
            while quantity > remaining_dice:
                quantity -= remaining_dice
                face += 1
            return {'type': 'bid', 'quantity': quantity, 'face': face}
        else:
            return {'type': 'challenge'}

class LiarDiceGameEnv:
    def __init__(self):
        self.game = LiarDiceGame()

    def reset(self):
        self.game.__init__()
        state = {
            'dice_count': self.game.get_dice_counts(),  # Ensure it's a dictionary
            'current_bid': self.game.get_current_bid(),
            'current_player': self.game.current_player,
            'last_action_was_challenge': self.game.last_action_was_challenge,
            'scores': self.game.scores,
        }
        return state

    def step(self, action):
        if action == 0:  # Bid
            quantity, face_value = self.game.random_bid()
            valid_bid = self.game.make_bid(self.game.current_player, quantity, face_value)
            reward = 0
            if not valid_bid:
                reward = -10  # Invalid bid penalty
        else:  # Challenge
            result = self.game.challenge(self.game.current_player)
            if "Challenge successful" in result:
                reward = 10
            else:
                reward = -10

        done = self.game.is_game_over()
        next_state = {
            'dice_count': self.game.get_dice_counts(),  # Ensure it's a dictionary
            'current_bid': self.game.get_current_bid(),
            'current_player': self.game.current_player,
            'last_action_was_challenge': self.game.last_action_was_challenge,
            'scores': self.game.scores,
        }
        return next_state, reward, done, {}

    def render(self):
        pass  # Optional: Add rendering logic if needed

    def get_winner(self):
        return self.game.get_winner()




# Custom Unpickler to handle loading with globals
class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == 'QLearningAgent':
            return QLearningAgent
        if name == 'DQNAgent':
            return DQNAgent
        if name == 'BayesianAgent':
            return BayesianAgent
        return super().find_class(module, name)

# Load the medium (Q-learning) agent
with open('medium_agent6.pkl', 'rb') as f:
    medium_agent = CustomUnpickler(f).load()

# Load the hard (DQN) agent's attributes
with open('hard_agent6.pkl', 'rb') as f:
    attributes = CustomUnpickler(f).load()

# Re-create the hard agent
hard_agent = DQNAgent(
    state_size=12,  # Adjusted state size based on the saved model
    action_size=attributes['action_size'],
    gamma=attributes['gamma'],
    epsilon=attributes['epsilon'],
    epsilon_min=attributes['epsilon_min'],
    epsilon_decay=attributes['epsilon_decay'],
    lr=attributes['lr'],
    batch_size=attributes['batch_size']
)


# Load the models
hard_agent.model.load_state_dict(torch.load('dqn_model6.pth'))
hard_agent.target_model.load_state_dict(torch.load('dqn_target_model6.pth'))

# Load the memory
hard_agent.memory = attributes['memory']

models = {
    'tutorial': None,
    'easy': None, 
    'medium': medium_agent,
    'hard': hard_agent,
}

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
                
            elif message == "challenge":
                result = game.challenge(1)
                user_message = "Challenge!"
                response_message = result

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

def get_ai_model(difficulty):
    return models.get(difficulty, models['medium'])  # Default to medium if difficulty not found

def generate_ai_response(game, room):
    difficulty = room.split('_')[0]  # Extract difficulty from room name
    model = models.get(difficulty, models['medium'])  # Default to medium if difficulty not found

    if difficulty == 'easy' or difficulty == 'tutorial':
        # Easy AI behavior
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
            
            if game.is_game_over():
                winner = game.get_winner()
                return f"Game over! {game.player_names[winner]} wins!"

            return f"Challenge! {result}"
    
    if game.is_game_over():
        winner = game.get_winner()
        return f"Game over! {game.player_names[winner]} wins!"

    state = game.get_game_state()
    if difficulty == 'medium' or difficulty == 'hard':
        action = model.get_action(state)
    
    if action == 0:  # Bid
        quantity, face_value = game.random_bid()
        game.make_bid(2, quantity, face_value)
        return f"Bid: {quantity} {face_value}s."
    else:  # Challenge
        result = game.challenge(2)
        if game.is_game_over():
            winner = game.get_winner()
            return f"Game over! {game.player_names[winner]} wins!"
        return f"Challenge! {result}"