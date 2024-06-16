import pickle
from q_learning_agent import QLearningAgent
from dqn_agent import DQNAgent, DQNetwork
from sarsa_agent import SARSAAgent
from mcts_agent import MCTSAgent
import numpy as np
from collections import defaultdict
import logging
import os

class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == 'QLearningAgent':
            return QLearningAgent
        if name == 'DQNetwork':
            return DQNetwork
        if name == 'DQNAgent':
            return DQNAgent
        if name == 'SARSAAgent':
            return SARSAAgent
        if name == 'MCTSAgent':
            return MCTSAgent
        return super().find_class(module, name)

def load_agents(easy_filename='q_learning_agent.pkl', medium_filename='dqn_agent.pkl', hard_filename='sarsa_agent.pkl'):
    logging.debug(f"Checking if file exists: {easy_filename}, {medium_filename}, {hard_filename}")

    # Check if file exists
    if not os.path.exists(easy_filename):
        logging.error(f"File does not exist: {easy_filename}")
        return None, None, None
    if not os.path.exists(medium_filename):
        logging.error(f"File does not exist: {medium_filename}")
        return None, None, None
    if not os.path.exists(hard_filename):
        logging.error(f"File does not exist: {hard_filename}")
        return None, None, None

    try:
        with open(easy_filename, 'rb') as f:
            q_table_dict = CustomUnpickler(f).load()
            easy_agent = QLearningAgent(state_size=7, action_size=132)
            easy_agent.q_table = defaultdict(lambda: np.zeros(easy_agent.action_size), q_table_dict)
    except Exception as e:
        logging.exception(f"Failed to load easy_agent from {easy_filename}")
        raise

    try:
        with open(medium_filename, 'rb') as f:
            medium_agent = CustomUnpickler(f).load()
            if not hasattr(medium_agent, 'network') or medium_agent.network is None:
                medium_agent.network = DQNetwork(medium_agent.state_size, medium_agent.action_size)
    except Exception as e:
        logging.exception(f"Failed to load medium_agent from {medium_filename}")
        raise

    try:
        with open(hard_filename, 'rb') as f:
            q_table_dict = CustomUnpickler(f).load()
            hard_agent = SARSAAgent(state_size=7, action_size=132)
            hard_agent.q_table = defaultdict(lambda: np.zeros(hard_agent.action_size), q_table_dict)
    except Exception as e:
        logging.exception(f"Failed to load hard_agent from {hard_filename}")
        raise

    return easy_agent, medium_agent, hard_agent
