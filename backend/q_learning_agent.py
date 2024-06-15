import logging
import numpy as np
from collections import defaultdict
import random
import pickle
import torch

class QLearningAgent:
    def __init__(self, state_size, action_size, alpha=0.1, gamma=0.99, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = defaultdict(lambda: torch.zeros(action_size, device=self.device))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def get_action(self, state):
        state_key = self.get_state_key(state)
        valid_actions = self.get_valid_actions(state)

        if np.random.rand() <= self.epsilon:
            action = random.choice(valid_actions)
        else:
            q_values = self.q_table[state_key]
            action = np.argmax([q_values[a] if a in valid_actions else -np.inf for a in range(self.action_size)])
        
        if action not in valid_actions:
            logging.error(f"Selected invalid action: {action}. Valid actions: {valid_actions}")
            action = random.choice(valid_actions)

        logging.debug(f"QLearningAgent selected action: {action}")
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

    def update_q_table(self, state, action, reward, next_state):
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        best_next_action = np.argmax(self.q_table[next_state_key])
        td_target = reward + self.gamma * self.q_table[next_state_key][best_next_action]
        td_error = td_target - self.q_table[state_key][action]
        self.q_table[state_key][action] += self.alpha * td_error

    def remember(self, state, action, reward, next_state, done):
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        best_next_action = np.argmax(self.q_table[next_state_key])
        td_target = reward + self.gamma * self.q_table[next_state_key][best_next_action]
        td_error = td_target - self.q_table[state_key][action]
        self.q_table[state_key][action] += self.alpha * td_error

    def get_state_key(self, state):
        return tuple(list(state["dice_count"]) + list(state["current_bid"]) + list(state["scores"]) + [state["current_player"]])

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(dict(self.q_table), f)

    def load(self, filename):
        with open(filename, 'rb') as f:
            q_table_dict = pickle.load(f)
            self.q_table = defaultdict(lambda: torch.zeros(self.action_size, device=self.device), q_table_dict)
