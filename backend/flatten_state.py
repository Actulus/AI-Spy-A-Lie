import numpy as np

def flatten_state(state):
    return np.concatenate([
        np.array(state['dice_count']),             # 2 elements (assuming 2 players)
        np.array([state['current_bid'][0], state['current_bid'][1]]),  # 2 elements
        np.array([state['current_player']]),       # 1 element
        np.array([state['last_action_was_challenge']]),  # 1 element
        np.array(list(state['scores'].values()))   # 2 elements
    ])


# Example length check
assert len(flatten_state({
    'dice_count': [5, 5],
    'current_bid': (1, 1),
    'current_player': 1,
    'last_action_was_challenge': False,
    'scores': {1: 0, 2: 0}
})) == 8
