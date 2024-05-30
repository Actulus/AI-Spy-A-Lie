import random

class LiarDiceGame:
    def __init__(self):
        self.dice_count = {1: 5, 2: 5}
        self.players = {1: [random.randint(1, 6) for _ in range(self.dice_count[1])], 
                        2: [random.randint(1, 6) for _ in range(self.dice_count[2])]}
        self.current_bid = (1, 1)  # Minimum bid to start each round
        self.current_player = 1
        self.last_action_was_challenge = False
        self.player_names = {1: 'Player 1', 2: 'Player 2'} # default player names

    def set_player_names(self, player1_name, player2_name):
        self.player_names[1] = player1_name
        self.player_names[2] = player2_name

    def roll_dice(self):
        for player in self.players:
            self.players[player] = [random.randint(1, 6) for _ in range(self.dice_count[player])]

    def reveal_dice(self):
        return self.players

    def make_bid(self, player, quantity, face_value):
        # total_dice = sum(self.dice_count.values())
        if face_value not in range(1, 7):
            return False
        
        if quantity > 10 or quantity < 1:
            return False

        # The initial bid of (1, 1) should be valid and subsequent bids should be higher
        if self.current_bid == (1, 1):
            # Allow the initial bid of (1, 1) to be placed again
            if quantity < 1 or face_value < 1:
                return False
        else:
            if quantity < self.current_bid[0] or (quantity == self.current_bid[0] and face_value <= self.current_bid[1]):
                return False

        self.current_bid = (quantity, face_value)
        self.last_action_was_challenge = False  # Reset the flag after a bid
        self.switch_player()
        return True


    def challenge(self, challenger):
        players_dice = self.reveal_dice()
        if self.current_bid[1] == 1:
            total_quantity = sum(dice.count(1) for dice in players_dice.values())
        else:
            total_quantity = sum(dice.count(self.current_bid[1]) + dice.count(1) for dice in players_dice.values())

        result = None
        dice_faces = {player: " ".join(str(die) for die in dice) for player, dice in players_dice.items()}

        if total_quantity >= self.current_bid[0]:
            # Switch player only after the challenge is handled
            self.switch_player()
            # Challenge failed: Challenger loses a die
            result = f"Challenge failed. Total dice count is {total_quantity}. {self.player_names[challenger]} loses a die.\n" \
                     f"{self.player_names[1]}'s dice: {dice_faces[1]}\n{self.player_names[2]}'s dice: {dice_faces[2]}"
            self.dice_count[challenger] -= 1
            self.players[challenger].pop()
        else:
            # Switch player only after the challenge is handled
            self.switch_player()
            # Challenge successful: Current player loses a die
            result = f"Challenge successful. Total dice count is {total_quantity}. {self.player_names[self.current_player]} loses a die.\n" \
                     f"{self.player_names[1]}'s dice: {dice_faces[1]}\n{self.player_names[2]}'s dice: {dice_faces[2]}"
            self.dice_count[self.current_player] -= 1
            self.players[self.current_player].pop()

        self.last_action_was_challenge = True  # Set the flag after a challenge
        self.current_bid = (0, 0)  # Reset the bid to minimum bid for new round
        self.roll_dice()

        # Check for game over condition before switching players
        if self.is_game_over():
            return result
        
        

        return result

    def switch_player(self):
        self.current_player = 1 if self.current_player == 2 else 2

    def is_game_over(self):
        return any(count == 0 for count in self.dice_count.values())

    def get_winner(self):
        if self.dice_count[1] == 0:
            return 2
        elif self.dice_count[2] == 0:
            return 1
        return None

    def random_bid(self):
        total_dice = 10
        
        min_quantity = self.current_bid[0] + 1
        if min_quantity > total_dice:
            min_quantity = total_dice

        quantity = random.randint(min_quantity, total_dice)
        face_value = random.randint(1, 6)
        return quantity, face_value

    def get_game_state(self):
        return {
            "dice_count": self.dice_count,
            "players": self.players,
            "current_bid": self.current_bid,
            "current_player": self.current_player,
            "last_action_was_challenge": self.last_action_was_challenge,
            "player_names": self.player_names,
        }