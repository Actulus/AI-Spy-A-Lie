import random

class ActionSpace:
    def __init__(self, action_types, quantities, face_values):
        self.action_types = action_types
        self.quantities = quantities
        self.face_values = face_values

    def sample(self):
        action_type = random.choice(self.action_types)
        quantity = random.choice(self.quantities)
        face_value = random.choice(self.face_values)
        return action_type, quantity, face_value

class LiarDiceGame:
    def __init__(self):
        self.dice_count = {1: 5, 2: 5}
        self.players = {1: [random.randint(1, 6) for _ in range(self.dice_count[1])], 
                        2: [random.randint(1, 6) for _ in range(self.dice_count[2])]}
        self.current_bid = (1, 1)  # Minimum bid to start each round
        self.current_player = 1
        self.last_action_was_challenge = False
        self.scores = {1: 0, 2: 0}
        self.player_names = {1: 'Player 1', 2: 'Player 2'} # default player names

        self.action_space = ActionSpace([0, 1], range(1, 11), range(1, 7))

    def set_player_names(self, player1_name, player2_name):
        self.player_names[1] = player1_name
        self.player_names[2] = player2_name

    def roll_dice(self):
        for player in self.players:
            self.players[player] = [random.randint(1, 6) for _ in range(self.dice_count[player])]

    def reveal_dice(self):
        return self.players

    def make_bid(self, player, quantity, face_value):
        if face_value not in range(1, 7):
            return False
        
        if quantity > 10 or quantity < 1:
            return False

        if self.current_bid == (1, 1):
            if quantity < 1 or face_value < 1:
                return False
        else:
            if quantity < self.current_bid[0] or (quantity == self.current_bid[0] and face_value <= self.current_bid[1]):
                return False

        self.current_bid = (quantity, face_value)
        self.last_action_was_challenge = False
        self.switch_player()
        return True
    
    def adjust_scores(self, winner, loser):
        self.scores[winner] += 100
        self.scores[loser] = max(0, self.scores[loser] - 100)


    def challenge(self, challenger):
        players_dice = self.reveal_dice()
        if self.current_bid[1] == 1:
            total_quantity = sum(dice.count(1) for dice in players_dice.values())
        else:
            total_quantity = sum(dice.count(self.current_bid[1]) + dice.count(1) for dice in players_dice.values())

        result = None
        dice_faces = {player: " ".join(str(die) for die in dice) for player, dice in players_dice.items()}

        if total_quantity >= self.current_bid[0]:
            self.switch_player()
            result = f"Challenge failed. Total dice count is {total_quantity}. {self.player_names[challenger]} loses a dice and 100 points. {self.player_names[self.current_player]} wins 100 points.\n" \
                     f"{self.player_names[1]}'s dice: {dice_faces[1]}\n{self.player_names[2]}'s dice: {dice_faces[2]}"
            if self.dice_count[challenger] > 0:
                self.dice_count[challenger] -= 1
                if self.players[challenger]:
                    self.players[challenger].pop()
            self.adjust_scores(self.current_player, challenger)
        else:
            self.switch_player()
            result = f"Challenge successful. Total dice count is {total_quantity}. {self.player_names[self.current_player]} loses a dice and 100 points. {self.player_names[challenger]} wins 100 points.\n" \
                     f"{self.player_names[1]}'s dice: {dice_faces[1]}\n{self.player_names[2]}'s dice: {dice_faces[2]}"
            if self.dice_count[self.current_player] > 0:
                self.dice_count[self.current_player] -= 1
                if self.players[self.current_player]:
                    self.players[self.current_player].pop()
            self.adjust_scores(challenger, self.current_player)

        self.last_action_was_challenge = True
        self.current_bid = (0, 0)
        self.roll_dice()

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
    
    def get_dice_counts(self):
        return self.dice_count
    
    def step(self, action):
        action_type, quantity, face_value = action

        if action_type == 0:  # Bid
            valid_bid = self.make_bid(self.current_player, quantity, face_value)
            if not valid_bid:
                return self.get_game_state(), -1, True, {}

            state = self.get_game_state()
            reward = 0
            done = self.is_game_over()
            return state, reward, done, {}

        elif action_type == 1:  # Challenge
            result = self.challenge(self.current_player)
            state = self.get_game_state()
            reward = 1 if 'successful' in result else -1
            done = self.is_game_over()
            return state, reward, done, {}


    def get_game_state(self):
        print(self.get_dice_counts())
        return {
            "dice_count": self.get_dice_counts(),
            "players": self.players,
            "current_bid": self.current_bid,
            "current_player": self.current_player,
            "last_action_was_challenge": self.last_action_was_challenge,
            "player_names": self.player_names,
            "scores": self.scores,
        }