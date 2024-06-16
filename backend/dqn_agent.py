import logging
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
import pickle

class DQNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_size)

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class DQNAgent:
    def __init__(self, state_size, action_size, network=None, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01, gamma=0.99, batch_size=32, memory_size=1000, target_update_freq=10):
        self.state_size = state_size
        self.action_size = action_size
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.gamma = gamma
        self.batch_size = batch_size
        self.memory = deque(maxlen=memory_size)
        self.target_update_freq = target_update_freq
        self.update_counter = 0

        if network:
            self.network = network
        else:
            self.network = DQNetwork(state_size, action_size)
        
        self.target_network = DQNetwork(state_size, action_size)
        self.update_target_network()

        self.optimizer = optim.Adam(self.network.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            action = random.randrange(self.action_size)
        else:
            state = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.network(state)
            action = q_values.max(1)[1].item()
        
        logging.debug(f"DQNAgent selected action: {action}")
        return action

    def get_valid_random_action(self, state):
        valid_actions = self.get_valid_actions(state)
        logging.debug(f"Valid actions for random selection: {valid_actions}")
        if valid_actions:
            return random.choice(valid_actions)
        return random.choice(range(self.action_size))

    def get_valid_actions(self, state):
        total_dice = sum(state["dice_count"])
        current_quantity, current_face_value = state["current_bid"]
        valid_actions = []
        for action in range(self.action_size):
            action_type = action // 66
            quantity = (action % 66) // 6 + 1
            face_value = action % 6 + 1
            if quantity > total_dice:
                continue  # Skip invalid quantities
            if action_type == 0 and (quantity > current_quantity or (quantity == current_quantity and face_value > current_face_value)):
                valid_actions.append(action)
            elif action_type == 1 and not state["last_action_was_challenge"]:
                valid_actions.append(action)
        logging.debug(f"Valid actions: {valid_actions}")
        return valid_actions

    def update_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def update_target_network(self):
        self.target_network.load_state_dict(self.network.state_dict())

    def remember(self, state, action, reward, next_state, done):
        state = np.array(list(state["dice_count"]) + list(state["current_bid"]) + list(state["scores"]) + [state["current_player"]])
        next_state = np.array(list(next_state["dice_count"]) + list(next_state["current_bid"]) + list(next_state["scores"]) + [next_state["current_player"]])
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        minibatch = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                next_state = torch.FloatTensor(next_state).unsqueeze(0)
                target = reward + self.gamma * torch.max(self.target_network(next_state)[0]).item()
            target_f = self.network(torch.FloatTensor(state).unsqueeze(0))
            target_f = target_f.cpu().detach().numpy()
            target_f[0][action] = target
            target_f = torch.FloatTensor(target_f)
            state = torch.FloatTensor(state).unsqueeze(0)
            output = self.network(state)
            loss = self.criterion(output, target_f)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
        
        self.update_counter += 1
        if self.update_counter % self.target_update_freq == 0:
            self.update_target_network()
        self.update_epsilon()

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
