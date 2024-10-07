import random
import json

class SimpleGridWorld:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.agent_position = (0, 0)  # Agent starts at top-left corner
        self.goal_position = (width - 1, height - 1)  # Goal position at bottom-right corner
        self.rewards = [[0] * width for _ in range(height)]
        self.rewards[self.goal_position[1]][self.goal_position[0]] = 100  # Reward at goal state
        self.q_values = [[[0, 0, 0, 0] for _ in range(width)] for _ in range(height)]  # Initialize Q-values

    def reset(self):
        self.agent_position = (0, 0)  # Reset agent position to top-left corner
        return self.agent_position

    def step(self, action):
        row, col = self.agent_position

        # Define action effects
        if action == 0:  # move up
            row -= 1
        elif action == 1:  # move down
            row += 1
        elif action == 2:  # move left
            col -= 1
        elif action == 3:  # move right
            col += 1

        # Ensure new position is within the grid
        row = max(0, min(row, self.height - 1))
        col = max(0, min(col, self.width - 1))

        # Update agent position
        self.agent_position = (row, col)

        # Check if the agent reached the goal
        if self.agent_position == self.goal_position:
            done = True
            reward = self.rewards[row][col]
        else:
            done = False
            reward = self.rewards[row][col]

        return self.agent_position, reward, done, {}

    def render(self):
        grid = [['O' for _ in range(self.width)] for _ in range(self.height)]
        grid[self.agent_position[1]][self.agent_position[0]] = 'A'  # Agent
        grid[self.goal_position[1]][self.goal_position[0]] = 'G'  # Goal

        for row in grid:
            print(' '.join(row))

    def choose_action(self, state, epsilon):
        row, col = state
        if random.uniform(0, 1) < epsilon:
            return random.choice(self.available_actions(state))
        else:
            return max(range(4), key=lambda x: self.q_values[row][col][x])

    def available_actions(self, state):
        row, col = state
        actions = []
        if row > 0:
            actions.append(0)  # Up
        if row < self.height - 1:
            actions.append(1)  # Down
        if col > 0:
            actions.append(2)  # Left
        if col < self.width - 1:
            actions.append(3)  # Right
        return actions

def train_rl_agent(env, num_episodes, initial_epsilon, alpha, gamma, max_steps=1000, epsilon_decay=0.995, min_epsilon=0.01):
    epsilon = initial_epsilon

    try:
        for episode in range(num_episodes):
            state = env.reset()
            done = False
            step = 0

            while not done and step < max_steps:
                row, col = state

                if random.random() < epsilon:
                    action = random.choice(env.available_actions(state))  # Explore
                else:
                    action = env.choose_action(state, epsilon)  # Exploit

                next_state, reward, done, _ = env.step(action)
                next_row, next_col = next_state

                # Update Q-values using the Q-learning update rule
                old_value = env.q_values[row][col][action]
                next_max = max(env.q_values[next_row][next_col])
                env.q_values[row][col][action] = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)

                state = next_state
                step += 1

            # Decay epsilon
            epsilon = max(min_epsilon, epsilon * epsilon_decay)

        return env.q_values

    except Exception as e:
        print("An error occurred during training:", e)

def test_rl_agent(env, q_values, epsilon):
    total_rewards = 0
    num_episodes = 10

    for _ in range(num_episodes):
        state = env.reset()
        done = False

        while not done:
            action = env.choose_action(state, epsilon)
            next_state, reward, done, _ = env.step(action)
            total_rewards += reward
            state = next_state

    return total_rewards / num_episodes

def save_q_values(q_values, filename):
    with open(filename, 'w') as f:
        json.dump(q_values, f)

def load_q_values(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def main():
    try:
        env = SimpleGridWorld(width=14, height=10)

        # Define training parameters
        num_episodes = 1000
        epsilon = 0.7
        alpha = 0.1
        gamma = 0.9

        q_values = train_rl_agent(env, num_episodes, epsilon, alpha, gamma)
        
        # Save Q-values to a JSON file
        save_q_values(q_values, 'q_values.json')
        
        # Load Q-values from file
        loaded_q_values = load_q_values('q_values.json')

        # Print the loaded Q-values to verify
        if loaded_q_values:
            print("Loaded Q-values:")
            for row, row_values in enumerate(loaded_q_values):
                for col, col_values in enumerate(row_values):
                    print("State: ({}, {}), Q-values: {}".format(row, col, col_values))
        else:
            print("No Q-values loaded.")
        
        # Print the learned Q-values in a structured format
        print("DEBUG ::: Learned Q-values:")
        for row in range(env.height):
            for col in range(env.width):
                state = (row, col)
                q_values_str = ", ".join("{:.2f}".format(q) for q in env.q_values[row][col])
                print("State: {}, Q-values: [{}]".format(state, q_values_str))

        
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
