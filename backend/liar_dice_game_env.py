from liars_dice_game_logic import LiarDiceGame

class LiarDiceGameEnv:
    def __init__(self):
        self.game = LiarDiceGame()

    def reset(self):
        self.game.__init__()
        return self.get_state()

    def get_state(self):
        return {
            'dice_count': self.game.get_dice_counts(),
            'current_bid': self.game.current_bid,
            'current_player': self.game.current_player,
            'last_action_was_challenge': self.game.last_action_was_challenge,
            'scores': self.game.scores,
        }

    def step(self, action):
        action_type, quantity, face_value = action

        if action_type == "bid":
            valid_bid = self.make_bid(self.current_player, quantity, face_value)
            if not valid_bid:
                return self.get_game_state(), -1, True, {}

            state = self.get_game_state()
            reward = 0
            done = self.is_game_over()
            return state, reward, done, {}

        elif action_type == "challenge":
            result = self.challenge(self.current_player)
            state = self.get_game_state()
            reward = 1 if 'successful' in result else -1
            done = self.is_game_over()
            return state, reward, done, {}

    def render(self):
        pass  # Optional: Add rendering logic if needed

    def get_winner(self):
        return self.game.get_winner()
