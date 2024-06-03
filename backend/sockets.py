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

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    
    def learn(self, state, action, reward, next_state):
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_size)
        
        best_next_action = np.argmax(self.q_table[next_state_key])
        td_target = reward + self.gamma * self.q_table[next_state_key][best_next_action]
        td_error = td_target - self.q_table[state_key][action]
        self.q_table[state_key][action] += self.alpha * td_error
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 24)
        self.fc2 = nn.Linear(24, 24)
        self.fc3 = nn.Linear(24, action_size)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

class DQNAgent:
    def __init__(self, state_size, action_size, gamma=0.99, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, lr=0.001, batch_size=64, memory_size=1000000):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=memory_size)
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.lr = lr
        self.batch_size = batch_size
        self.model = DQN(state_size, action_size)
        self.target_model = DQN(state_size, action_size)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        self.update_target_model()
    
    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((self.flatten_state(state), action, reward, self.flatten_state(next_state), done))
    
    def flatten_state(self, state):
        return np.concatenate([
            np.array(list(state['dice_count'].values())), 
            np.array(state['current_bid']), 
            np.array([state['current_player']]), 
            np.array([state['last_action_was_challenge']]), 
            np.array(list(state['scores'].values()))
        ])

    def get_action(self, state):
        state = self.flatten_state(state)
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        state = torch.FloatTensor(state)
        with torch.no_grad():
            q_values = self.model(state)
        return np.argmax(q_values.cpu().numpy())
    
    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        minibatch = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state, done in minibatch:
            state = torch.FloatTensor(state)
            next_state = torch.FloatTensor(next_state)
            target = self.model(state).cpu().data.numpy()
            if done:
                target[action] = reward
            else:
                with torch.no_grad():
                    t = self.target_model(next_state)
                target[action] = reward + self.gamma * np.amax(t.cpu().numpy())
            target = torch.FloatTensor(target)
            self.optimizer.zero_grad()
            output = self.model(state)
            loss = F.mse_loss(output, target)
            loss.backward()
            self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def learn(self, state, action, reward, next_state, done):
        self.remember(state, action, reward, next_state, done)
        self.replay()

class EasyAI:
    def __init__(self, game):
        self.game = game

    def get_action(self, state):
        if self.game.is_game_over():
            winner = self.game.get_winner()
            return f"Game over! {self.game.player_names[winner]} wins!"
        
        if self.game.last_action_was_challenge or self.game.current_bid == (1, 1):
            action = 'bid'  # Force bid after challenge or for the first move
        else:
            action = random.choice(['bid', 'challenge'])

        # if current bid is 10 6s, challenge
        if self.game.current_bid[0] == 10:
            action = 'challenge'

        if action == 'bid':
            quantity, face_value = self.game.random_bid()
            self.game.make_bid(2, quantity, face_value)  # Assuming player 2 is the AI
            return 0  # Bid action
        else:
            result = self.game.challenge(2)
            
            if self.game.is_game_over():
                winner = self.game.get_winner()
                return f"Game over! {self.game.player_names[winner]} wins!"

            return 1  # Challenge action

# Custom Unpickler to handle loading with globals
class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == 'QLearningAgent':
            return QLearningAgent
        return super().find_class(module, name)

# Load the medium (Q-learning) agent
with open('medium_agent.pkl', 'rb') as f:
    medium_agent = CustomUnpickler(f).load()

# Load the hard (DQN) agent's attributes
with open('hard_agent.pkl', 'rb') as f:
    attributes = CustomUnpickler(f).load()

# Re-create the hard agent
hard_agent = DQNAgent(
    state_size=attributes['state_size'],
    action_size=attributes['action_size'],
    gamma=attributes['gamma'],
    epsilon=attributes['epsilon'],
    epsilon_min=attributes['epsilon_min'],
    epsilon_decay=attributes['epsilon_decay'],
    lr=attributes['lr'],
    batch_size=attributes['batch_size']
)

# Load the models
hard_agent.model.load_state_dict(torch.load('dqn_model.pth'))
hard_agent.target_model.load_state_dict(torch.load('dqn_target_model.pth'))

# Load the memory
hard_agent.memory = attributes['memory']

models = {
    'easy': EasyAI,  # Assuming EasyAI class is defined
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
    model = get_ai_model(difficulty)

    if difficulty == 'easy':
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
    if difficulty == 'medium':
        action = model.get_action(state)
    elif difficulty == 'hard':
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
