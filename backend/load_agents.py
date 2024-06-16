import pickle
from q_learning_agent import QLearningAgent
from dqn_agent import DQNAgent, DQNetwork
from sarsa_agent import SARSAAgent
from mcts_agent import MCTSAgent
import numpy as np
from collections import defaultdict
import logging
import os
import torch

logging.basicConfig(level=logging.DEBUG)

class CustomUnpickler(pickle.Unpickler):
    def __init__(self, *args, map_location='cpu', **kwargs):
        self._map_location = map_location
        super().__init__(*args, **kwargs)

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

    def persistent_load(self, saved_id):
        if isinstance(saved_id, tuple):
            if saved_id[0] == 'storage':
                storage_type, key, location, storage_view, numel = saved_id
                if 'cuda' in location:
                    location = 'cpu'
                return super().persistent_load((storage_type, key, location, storage_view, numel))
        return super().persistent_load(saved_id)

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
            q_table_dict = CustomUnpickler(f, map_location='cpu').load()
            easy_agent = QLearningAgent(state_size=7, action_size=132)
            easy_agent.q_table = defaultdict(lambda: np.zeros(easy_agent.action_size), q_table_dict)
            logging.debug(f"Easy agent loaded successfully from {easy_filename}")
    except Exception as e:
        logging.exception(f"Failed to load easy_agent from {easy_filename}")
        raise

    try:
        with open(medium_filename, 'rb') as f:
            logging.debug("Loading medium agent from DQN agent file")
            medium_agent = CustomUnpickler(f, map_location='cpu').load()
            logging.debug(f"Medium agent loaded: {medium_agent}")
            if not hasattr(medium_agent, 'network') or medium_agent.network is None:
                logging.debug("Initializing DQNetwork for medium agent")
                medium_agent.network = DQNetwork(medium_agent.state_size, medium_agent.action_size)
                logging.debug("Loading state dict for medium agent's network")
                state_dict = torch.load(f, map_location='cpu')
                medium_agent.network.load_state_dict(state_dict)
            else:
                logging.debug(f"Medium agent's network is already initialized: {medium_agent.network}")
    except Exception as e:
        logging.exception(f"Failed to load medium_agent from {medium_filename}")
        raise

    try:
        with open(hard_filename, 'rb') as f:
            logging.debug("Loading hard agent from SARSA agent file")
            q_table_dict = CustomUnpickler(f, map_location='cpu').load()
            hard_agent = SARSAAgent(state_size=7, action_size=132)
            logging.debug("Converting q_table_dict items to tensors for hard agent")
            hard_agent.q_table = defaultdict(lambda: torch.zeros(hard_agent.action_size, device=hard_agent.device),
                                             {k: (torch.tensor(v, device=hard_agent.device) if not isinstance(v, dict) else
                                                  {sub_k: torch.tensor(sub_v, device=hard_agent.device) for sub_k, sub_v in v.items()})
                                              for k, v in q_table_dict.items()})
            logging.debug(f"Hard agent loaded successfully from {hard_filename}")
    except Exception as e:
        logging.exception(f"Failed to load hard_agent from {hard_filename}")
        raise

    return easy_agent, medium_agent, hard_agent
# Check current working directory
logging.debug(f"Current working directory: {os.getcwd()}")

try:
    easy_agent, medium_agent, hard_agent = load_agents()
    logging.debug("Agents loaded successfully")
except Exception as e:
    logging.exception("Failed to load agents")
    raise
