import logging
import numpy as np
from collections import defaultdict
import random
import torch
import pickle

class SARSAAgent:
    def __init__(self, state_size, action_size, alpha=0.1, gamma=0.99, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = defaultdict(lambda: np.zeros(action_size))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def get_action(self, state):
        if np.random.rand() <= self.epsilon:
            action = self.get_valid_random_action(state)
        else:
            state_key = self.get_state_key(state)
            q_values = self.q_table[state_key]
            valid_actions = self.get_valid_actions(state)
            if not valid_actions:
                action = random.choice(range(self.action_size))
            else:
                action = max(valid_actions, key=lambda a: q_values[a])
        
        logging.debug(f"SARSAAgent selected action: {action}")
        return action

    def get_valid_random_action(self, state):
        valid_actions = self.get_valid_actions(state)
        logging.debug(f"Valid actions for random selection: {valid_actions}")
        if valid_actions:
            return random.choice(valid_actions)
        return random.choice(range(self.action_size))
    
    def get_valid_actions(self, state):
        current_quantity, current_face_value = state["current_bid"]
        valid_actions = []
        for action in range(self.action_size):
            action_type = action // 66
            quantity = (action % 66) // 6 + 1
            face_value = action % 6 + 1
            if action_type == 0 and (quantity > current_quantity or (quantity == current_quantity and face_value > current_face_value)):
                valid_actions.append(action)
            elif action_type == 1 and not state["last_action_was_challenge"]:
                valid_actions.append(action)
        logging.debug(f"Valid actions: {valid_actions}")
        return valid_actions

    def update_q_table(self, state, action, reward, next_state, next_action):
        state = torch.tensor(state, device=self.device, dtype=torch.float32)
        next_state = torch.tensor(next_state, device=self.device, dtype=torch.float32)
        td_target = reward + self.gamma * self.q_table[tuple(next_state.cpu().numpy())][next_action]
        td_error = td_target - self.q_table[tuple(state.cpu().numpy())][action]
        self.q_table[tuple(state.cpu().numpy())][action] += self.alpha * td_error

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(dict(self.q_table), f)

    def load(self, filename):
        with open(filename, 'rb') as f:
            self.q_table = defaultdict(lambda: np.zeros(self.action_size), pickle.load(f))

    def get_state_key(self, state):
        return tuple(list(state["dice_count"]) + list(state["current_bid"]) + list(state["scores"]) + [state["current_player"]])
