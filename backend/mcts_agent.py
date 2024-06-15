import pickle

class MCTSAgent:
    def __init__(self, num_simulations=100):
        self.num_simulations = num_simulations

    def select_action(self, state, env):
        root = Node(state, None, None, env)
        for _ in range(self.num_simulations):
            leaf = self.traverse(root, env)
            reward = self.rollout(leaf.state, env)
            self.backpropagate(leaf, reward)
        return self.best_action(root)

    def traverse(self, node, env):
        while not node.is_terminal():
            if node.is_fully_expanded():
                node = self.best_child(node)
            else:
                return self.expand(node, env)
        return node

    def expand(self, node, env):
        action = node.untried_actions.pop()
        action_type, quantity, face_value = action // 66, (action % 66) // 6, action % 6 + 1
        next_state, _, done, _ = env.step((action_type, quantity, face_value))
        child_node = Node(next_state, node, action, env)
        node.children.append(child_node)
        return child_node

    def rollout(self, state, env):
        current_state = state
        done = False
        total_reward = 0
        while not done:
            action = env.action_space.sample()
            action_type, quantity, face_value = action
            next_state, reward, done, _ = env.step((action_type, quantity, face_value))
            current_state = next_state
            total_reward += reward
        return total_reward

    def backpropagate(self, node, reward):
        while node is not None:
            node.visits += 1
            node.reward += reward
            node = node.parent

    def best_action(self, node):
        best_child = max(node.children, key=lambda child: child.reward / child.visits)
        return best_child.action

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

class Node:
    def __init__(self, state, parent, action, env):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.reward = 0
        self.untried_actions = list(range(2 * 11 * 6))  # Assuming 2 action types, 11 quantities, 6 face values
        self.env = env
        self.action = action

    def is_terminal(self):
        return self.env.is_game_over()

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self):
        return max(self.children, key=lambda child: child.reward / child.visits)
