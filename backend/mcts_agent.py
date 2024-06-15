import logging

class MCTSAgent:
    def __init__(self, num_simulations=100):
        self.num_simulations = num_simulations

    def select_action(self, state, env):
        root = Node(state, None, None, env)
        for _ in range(self.num_simulations):
            leaf = self.traverse(root, env)
            reward = self.simulate(leaf.state, env)
            self.backpropagate(leaf, reward)
        best_action_node = self.best_action(root)
        logging.info(f"Best action node: {best_action_node.action}, Reward: {best_action_node.reward}, Visits: {best_action_node.visits}")
        return best_action_node.action

    def traverse(self, node, env):
        while not node.is_terminal():
            if node.is_fully_expanded():
                node = self.best_child(node)
            else:
                return self.expand(node, env)
        return node

    def expand(self, node, env):
        action = node.untried_actions.pop()
        action_type, quantity, face_value = decode_action(action)
        next_state, _, done, _ = env.step((action_type, quantity, face_value))
        child_node = Node(next_state, node, action, env)
        node.children.append(child_node)
        return child_node

    def simulate(self, state, env):
        action = env.action_space.sample()  # Or use a more sophisticated strategy
        action_type, quantity, face_value = decode_action(action)
        if not is_valid_action(action_type, quantity, face_value, state):
            return 0
        next_state, reward, done, _ = env.step((action_type, quantity, face_value))
        return reward

    def backpropagate(self, node, reward):
        while node is not None:
            node.visits += 1
            node.reward += reward
            node = node.parent

    def best_action(self, node):
        return max(node.children, key=lambda child: child.reward / child.visits)


class Node:
    def __init__(self, state, parent, action, env):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.reward = 0
        self.untried_actions = self.get_untried_actions(state)
        self.env = env
        self.action = action

    def is_terminal(self):
        return self.env.is_game_over()

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self):
        return max(self.children, key=lambda child: child.reward / child.visits)

    def get_untried_actions(self, state):
        actions = []
        total_dice = sum(state["dice_count"])
        current_quantity, current_face_value = state["current_bid"]

        for action in range(2 * 11 * 6):  # Assuming 2 action types, 11 quantities, 6 face values
            action_type, quantity, face_value = decode_action(action)
            if action_type == 0:  # Bid
                if 1 <= quantity <= total_dice and 1 <= face_value <= 6:
                    if quantity > current_quantity or (quantity == current_quantity and face_value > current_face_value):
                        actions.append(action)
            elif action_type == 1:  # Challenge
                if not state["last_action_was_challenge"]:
                    actions.append(action)
        return actions



def decode_action(action):
    if isinstance(action, tuple):
        return action
    else:
        action_type = action // 66
        quantity = (action % 66) // 6 + 1
        face_value = action % 6 + 1
        return action_type, quantity, face_value

def is_valid_action(action_type, quantity, face_value, state):
    current_quantity, current_face_value = state["current_bid"]
    total_dice = sum(state["dice_count"])

    if action_type == 0:  # Bid
        if quantity > total_dice or quantity < 1:
            return False
        if face_value < 1 or face_value > 6:
            return False
        if quantity < current_quantity or (
            quantity == current_quantity and face_value <= current_face_value
        ):
            return False
    elif action_type == 1:  # Challenge
        if state["last_action_was_challenge"]:
            return False
        if current_quantity == 1 and current_face_value == 1:
            return True  # Always valid to challenge the first bid
        if quantity > total_dice:
            return False  # Quantity should not exceed total dice
    return True
