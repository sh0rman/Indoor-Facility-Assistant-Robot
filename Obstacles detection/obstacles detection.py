from AriaPy import *
import sys

# Define a custom task for printing robot position information
class PrintingTask:
    def __init__(self, robot):
        self.myRobot = robot
        robot.addSensorInterpTask("PrintingTask", 50, self.doTask)

    def doTask(self):
        print("x %6.1f  y %6.1f  th  %6.1f vel %7.1f mpacs %3d" % (self.myRobot.getX(), self.myRobot.getY(), self.myRobot.getTh(), self.myRobot.getVel(), self.myRobot.getMotorPacCount()))


# Initialize ARIA
Aria_init()

# Create argument parser and load default arguments
parser = ArArgumentParser(sys.argv)
robot = ArRobot()
conn = ArRobotConnector(parser, robot)

if not conn.connectRobot():
    print("Could not connect to robot, exiting")
    Aria_exit(1)

# Parse arguments
if not Aria_parseArgs():
    Aria_logOptions()
    Aria_exit(1)

# Most robots have sonar:
print("Creating sonar object...")
sonar = ArSonarDevice()
robot.addRangeDevice(sonar)


# Some robots have laser rangefinders (enabled in robot's parameter .p file or
# with -connectLaser command line argument):
laserConn = ArLaserConnector(parser, robot, conn)
if not laserConn.connectLasers():
    print ("Warning: could not connect to laser(s).")

# Add custom printing task for position information
printTask = PrintingTask(robot)

# Define actions for obstacle avoidance
stallRecover = ArActionStallRecover()
avoidFront = ArActionAvoidFront()
limitFront = ArActionLimiterForwards("limitFront", 300, 600, 250)
limitBack = ArActionLimiterBackwards()
constVel = ArActionConstantVelocity()

# Add actions to ArRobot
robot.addAction(stallRecover, 100)
robot.addAction(avoidFront, 50)
robot.addAction(limitFront, 30)  # Increase priority to allow more aggressive avoidance
robot.addAction(limitBack, 20)
robot.addAction(constVel, 10)

# Enable robot motors
print("Enabling motors...")
robot.enableMotors()

# Run robot thread here in the main thread
print("Running robot...")
robot.run(1)

print("Goodbye.")
Aria_exit(0)

