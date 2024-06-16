import pickle
from ai_models.q_learning_agent import QLearningAgent
from ai_models.dqn_agent import DQNAgent, DQNetwork
from ai_models.sarsa_agent import SARSAAgent
from ai_models.mcts_agent import MCTSAgent
import numpy as np
from collections import defaultdict

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

def load_agents(easy_filename='./ai_models/q_learning_agent.pkl', medium_filename='./ai_models/dqn_agent.pkl', hard_filename='./ai_models/sarsa_agent.pkl'):
    with open(easy_filename, 'rb') as f:
        q_table_dict = CustomUnpickler(f).load()
        easy_agent = QLearningAgent(state_size=7, action_size=132)  # Adjust state_size and action_size accordingly
        easy_agent.q_table = defaultdict(lambda: np.zeros(easy_agent.action_size), q_table_dict)
    
    with open(medium_filename, 'rb') as f:
        medium_agent = CustomUnpickler(f).load()
        if not hasattr(medium_agent, 'network') or medium_agent.network is None:
            medium_agent.network = DQNetwork(medium_agent.state_size, medium_agent.action_size)  # Ensure network is set
    
    with open(hard_filename, 'rb') as f:
        q_table_dict = CustomUnpickler(f).load()
        hard_agent = SARSAAgent(state_size=7, action_size=132)  # Adjust state_size and action_size accordingly
        hard_agent.q_table = defaultdict(lambda: np.zeros(hard_agent.action_size), q_table_dict)
    
    return easy_agent, medium_agent, hard_agent