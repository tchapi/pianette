import serial
import time
import random

usleep = lambda x: time.sleep(x/1000000.0)

# Number of µsecs that we need to wait between commands from controller
usecs_between_data = 1

class ConsoleController:

  serialConnection = False;

  def __init__(self, stateController):
    self.stateController = stateController
    self.serialConnection = serial.Serial('/dev/ttyACM0', 115200)
    random.seed()

  # Single buttons
  def sendX(self):
    ser.write(b'\xFF\xBF');
  def sendO(self):
    ser.write(b'\xFF\xDF');
  def sendSquare(self):
    ser.write(b'\xFF\x7F');
  def sendTriangle(self):
    ser.write(b'\xFF\xEF');

  def sendStart(self):
    ser.write(b'\xF7\xFF')
  def sendSelect(self):
    ser.write(b'\xF7\xFE')

  def sendUp(self):
    ser.write(b'\xEF\xFF');
  def sendDown(self):
    ser.write(b'\xBF\xFF');
  def sendLeft(self):
    ser.write(b'\x7F\xFF');
  def sendRight(self):
    ser.write(b'\xDF\xFF');

  # Simple movement combos
  def sendDownRight(self):
    # RIGHT + DOWN
    ser.write(b'\x9F\xFF')
  def sendDownLeft(self):
    # LEFT + DOWN
    ser.write(b'\x3F\xFF')
  def sendUpRight(self):
    # RIGHT + UP
    ser.write(b'\xCF\xFF')
  def sendUpLeft(self):
    # LEFT + UP
    ser.write(b'\x6F\xFF')


# FIX ME FIX ME
  # Nice combos
  def sendHadouken(self):
    # LEFT + UP
    ser.write(b'\xFF\xFF')

  def sendTatsumaki(self):
    # LEFT + UP
    ser.write(b'\xFF\xFF')

  def sendUltra(self):
    # LEFT + UP
    ser.write(b'\xFF\xFF')
# FIX ME FIX ME

  # Send a reset byte couple, going back to the menus
  def sendReset(self):
    ser.write(b'\x00\x00');

  # Methods 
  def restartFresh(self):
    # Back to main menu
    self.sendReset()
    usleep(usecs_between_data)
    self.sendStart()
    usleep(usecs_between_data)
    # Choose "VERSUS" mode
    self.chooseVersusModeFromMenu()
    self.newGameFromVersusMenu()
    
  def restartSuperFresh(self):
    # Back to start
    self.sendReset()
    usleep(usecs_between_data)
    self.restartFresh()
    
  def chooseVersusModeFromMenu(self):
    self.sendLeft())
    usleep(usecs_between_data)
    self.sendX()
    usleep(usecs_between_data)

  def newGameFromVersusMenu(self):
    # Choose random character
    if (self.stateController.playerOne == True):
      self.sendRight()
    else:
      self.sendLeft()
    usleep(usecs_between_data)
    self.sendUp()
    usleep(usecs_between_data)
    self.sendUp()
    usleep(usecs_between_data)
    # Acknowledge handicap
    self.sendX()
    usleep(usecs_between_data)
    # Acknowledge Battle field - we choose a random stage going right >>
    stage = random.randint(1, 10)
    for x in xrange(1,stage):
      self.sendRight()
      usleep(usecs_between_data)
    self.sendX()
    usleep(usecs_between_data)

    # Wait two seconds for cinematic
    time.sleep(2)

    # FIGHT !!!!

  def createStateBytes(self, channel):
    print("Sending state :", self.stateController)
    
    self.state_as_bytes = []

    self.state_as_bytes.append( # Data byte 1
      (0b00000001 if self.stateController.state["SELECT"] else 0) |
      (0b00001000 if self.stateController.state["START"] else 0) |
      (0b00010000 if self.stateController.state["UP"] else 0) |
      (0b00100000 if self.stateController.state["RIGHT"] else 0) |
      (0b01000000 if self.stateController.state["DOWN"] else 0) |
      (0b10000000 if self.stateController.state["LEFT"] else 0)
    )

    self.state_as_bytes.append( # Data byte 2
      (0b00010000 if self.stateController.state["T"] else 0) |
      (0b00100000 if self.stateController.state["O"] else 0) |
      (0b01000000 if self.stateController.state["X"] else 0) |
      (0b10000000 if self.stateController.state["S"] else 0)
    )


    # Sends the command out to the Arduino
    # FIX ME ???
    ser.write(self.state_as_bytes)

