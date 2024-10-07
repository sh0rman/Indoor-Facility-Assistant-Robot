from AriaPy import *
import sys   
import AStra2

path = AStra2.a_star(AStra2.my_maze, (6, 12), (2, 1), AStra2.heuristic)  # Find the optimal path using A* algorithm

# Display the optimal path
print("Optimal Path:")
for cell in path:
    print(cell)

def turn(robot, mov_angle):
    robot.lock()
    robot.setHeading(mov_angle)
    robot.unlock()
    ArUtil_sleep(2000)
def walk(robot, mov_distance):
    robot.lock()
    robot.move(mov_distance)
    robot.unlock()
    ArUtil_sleep(2000)

def movement(robot, mov_distance, mov_angle):
    #print(f"Moving {mov_distance} at {mov_angle}")

    robot.lock()
    robot.move(mov_distance)
    robot.unlock()

    ArUtil_sleep(3000)  # Sleep to ensure each movement completes

    robot.lock()
    robot.setHeading(mov_angle)
    robot.unlock()

    ArUtil_sleep(500)  # Sleep to ensure each movement completes

def main_movements(robot, path):
    for i in range(len(path) - 1):
        current = path[i]
        next = path[i + 1]
        print("moving to", next)

        if next[0] < current[0]:
            print('move right') #right
            #movement(robot, 0, 0)
            #movement(robot, 400, 0)
            turn(robot, 0)
            walk(robot,400)
        elif next[0] > current[0]:
            print('move left') #left
            #movement(robot, 0, 180)
            #movement(robot, 400, 180)
            turn(robot, 180)
            walk(robot,400)

        elif next[1] < current[1]:
            print('move up') #up
            #movement(robot, 0, 90)
            #movement(robot, 200, 90)
            turn(robot, 90)
            walk(robot,250)
        elif next[1] > current[1]:
            print('move down') #down
            #movement(robot, 0, -90)
            #movement(robot, 200, -90)
            turn(robot, -90)
            walk(robot,250)
    

    robot.lock()
    robot.stop()
    robot.unlock()

# Initialize Aria and create robot instance
Aria_init()

parser = ArArgumentParser(sys.argv)
parser.loadDefaultArguments()

robot = ArRobot()
con = ArRobotConnector(parser, robot)
    
if not Aria_parseArgs():
    Aria_logOptions()
    Aria_exit(1)

if not con.connectRobot():
    print("Could not connect to robot, exiting")
    Aria_exit(1)

stallRecover = ArActionStallRecover()
avoidFront = ArActionAvoidFront()
limitFront = ArActionLimiterForwards("limitFront", 300, 600, 250)
limitBack = ArActionLimiterBackwards()

robot.addAction(stallRecover, 100)
robot.addAction(avoidFront, 50)
robot.addAction(limitFront, 30)
robot.addAction(limitBack, 20)

sonar = ArSonarDevice()
robot.addRangeDevice(sonar)

laserConn = ArLaserConnector(parser, robot, con)
if not laserConn.connectLasers():
    print("Warning: could not connect to laser(s).")

robot.enableMotors()
robot.runAsync(True)  # Keep the robot running in the background

main_movements(robot, path)

Aria_exit()  # Exit Aria after all movements are done
