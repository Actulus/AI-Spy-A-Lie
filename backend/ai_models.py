# backend/ai_models.py

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque
import random
import numpy as np

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
