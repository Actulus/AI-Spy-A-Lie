import logging
import numpy as np

class BayesianAgent:
    def __init__(self, num_players, num_dice):
        self.num_players = num_players
        self.num_dice = num_dice
        self.beliefs = self.initialize_beliefs()

    def initialize_beliefs(self):
        beliefs = np.ones((self.num_players, 6)) / 6
        return beliefs

    def update_beliefs(self, state, action):
        current_player = state['current_player']
        if action['type'] == 'bid':
            bid_quantity, bid_face = action['quantity'], action['face']
            for player in range(self.num_players):
                if player != current_player:
                    self.beliefs[player, bid_face - 1] *= bid_quantity / self.num_dice
                    self.beliefs[player] /= np.sum(self.beliefs[player])
        elif action['type'] == 'challenge':
            challenged_bid = state['current_bid']
            actual_quantity = sum(state['players'][player].count(challenged_bid[1]) for player in range(self.num_players))
            if actual_quantity >= challenged_bid[0]:
                for player in range(self.num_players):
                    if player != current_player:
                        self.beliefs[player, challenged_bid[1] - 1] *= actual_quantity / self.num_dice
                        self.beliefs[player] /= np.sum(self.beliefs[player])
            else:
                for player in range(self.num_players):
                    if player != current_player:
                        self.beliefs[player, challenged_bid[1] - 1] *= (self.num_dice - actual_quantity) / self.num_dice
                        self.beliefs[player] /= np.sum(self.beliefs[player])

    def get_action(self, state):
        current_bid = state['current_bid']
        if current_bid == (1, 1):
            return {'type': 'bid', 'quantity': 1, 'face': 1}

        current_player = state['current_player']
        total_dice = self.num_dice * self.num_players

        # Ensure `current_bid[1]` is within valid range
        if not (1 <= current_bid[1] <= 6):
            logging.error(f"Invalid bid face value: {current_bid[1]}")
            return {'type': 'challenge'}

        dice_count = state['dice_count']
        if not (0 <= current_bid[1] - 1 < len(dice_count)):
            logging.error(f"Invalid dice count index for bid face value: {current_bid[1]}")
            return {'type': 'challenge'}

        remaining_dice = total_dice - dice_count[current_bid[1] - 1]
        prob_bid_correct = np.prod([np.sum(self.beliefs[player, current_bid[1] - 1:]) for player in range(self.num_players) if player != current_player])

        if prob_bid_correct > 0.7:
            quantity = current_bid[0] + 1
            face = current_bid[1]
            while quantity > remaining_dice:
                quantity -= remaining_dice
                face += 1
            if face > 6:
                logging.error(f"Invalid face value after adjustment: {face}")
                return {'type': 'challenge'}
            return {'type': 'bid', 'quantity': quantity, 'face': face}
        else:
            return {'type': 'challenge'}
