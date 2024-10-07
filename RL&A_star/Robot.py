from AriaPy import *
import sys
from Rein_Learn import SimpleGridWorld, train_rl_agent, load_q_values
import A_Star_Search as A_Star_Search

# Define your maze size and create a GridWorld object
width = 14
height = 10
grid_world = SimpleGridWorld(width, height)

# Train the RL agent to learn Q-values
q_values = train_rl_agent(grid_world, num_episodes=1000, initial_epsilon=0.1, alpha=0.1, gamma=0.9)

# Use the learned Q-values as the heuristic function in the A* algorithm
def h_q_values(cell1, cell2):
    row1, col1 = cell1
    row2, col2 = cell2
    key1 = "({}, {})".format(row1, col1)
    key2 = "({}, {})".format(row2, col2)
    return max(q_values[row1][col1]) + max(q_values[row2][col2])

# Define the start and end nodes for A*
start_node = (0, 0)
end_node = (9, 13)

# Find the optimal path using A* algorithm with Q-values as the heuristic
path = A_Star_Search.a_star(A_Star_Search.my_maze, start_node, end_node, heuristic=h_q_values)

# Display the optimal path
print("Optimal Path:")
for cell in path:
    print(cell)


class PrintingTask:
    def __init__(self, robot, goal_pose):
        self.myRobot = robot
        self.myGoal = goal_pose
        robot.addSensorInterpTask("PrintingTask", 50, self.doTask)

    def doTask(self):
        print("x %6.1f  y %6.1f  th  %6.1f vel %7.1f mpacs %3d" % (self.myRobot.getX(), self.myRobot.getY(), self.myRobot.getTh(), self.myRobot.getVel(), self.myRobot.getMotorPacCount()))
        if self.myRobot.getX() >= self.myGoal.getX() and self.myRobot.getY() >= self.myGoal.getY(): 
            print("Goal Reached ^_^")
            self.myRobot.stop()

Aria_init()

parser = ArArgumentParser(sys.argv)
parser.loadDefaultArguments()

# Create a robot object:
robot = ArRobot()

# Create a "simple connector" object and connect to either the simulator or the robot. Unlike the C++ API which takes int and char* pointers, the Python constructor just takes argv as a list.
print("Hey There...")

con = ArRobotConnector(parser, robot)
if not Aria_parseArgs():
    Aria_logOptions()
    Aria_exit(1)

if not con.connectRobot():
    print("Could not connect to robot, exiting")
    Aria_exit(1)

# Define actions for obstacle avoidance
stallRecover = ArActionStallRecover()
avoidFront = ArActionAvoidFront()
limitFront = ArActionLimiterForwards("limitFront", 300, 600, 250)
limitBack = ArActionLimiterBackwards()

# Add actions to ArRobot
robot.addAction(stallRecover, 100)
robot.addAction(avoidFront, 50)
robot.addAction(limitFront, 30)
robot.addAction(limitBack, 20)

# Run the robot threads in the background:
print("Running...")
sonar = ArSonarDevice()
robot.addRangeDevice(sonar)

# Some robots have laser rangefinders (enabled in robot's parameter .p file or with -connectLaser command line argument):
laserConn = ArLaserConnector(parser, robot, con)
if not laserConn.connectLasers():
    print("Warning: could not connect to laser(s).")

print("Connected to the robot. (Press Ctrl-C to exit)")

# Get goal coordinates from the start and end nodes
goal_x_start, goal_y_start = start_node
goal_x_end, goal_y_end = end_node

# Create ArPose objects for start and end nodes
goal_pose_start = ArPose(goal_x_start, goal_y_start)
goal_pose_end = ArPose(goal_x_end, goal_y_end)

# Set up action for going to the goal
goto_action = ArActionGoto("goto", goal_pose_end, 0)
robot.addAction(goto_action, 0)

# Initialize PrintingTask
printTask = PrintingTask(robot, goal_pose_end)

# Enable motors and run the robot
robot.enableMotors()
robot.run(1)
print("Disconnected. Goodbye.")

Aria_exit(0)
