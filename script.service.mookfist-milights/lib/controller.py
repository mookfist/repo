import threading
from utils import Logger
from mookfist_lled_controller import WifiBridge
from collections import deque
import socket
import time

class Controller(threading.Thread):

  def __init__(self, *args, **kwargs):
    super(Controller, self).__init__()

    self._queue = deque([])
    self._bridge_ip = kwargs.get('bridge_ip', None)
    self._bridge_port = kwargs.get('bridge_port', None)
    self._bridge_version = kwargs.get('bridge_version', None)
    self._pause = kwargs.get('pause', 100)
    self._repeat = kwargs.get('repeat', 1)

    self._running = False
    self._init_bridge = True

    self.logger = Logger('mookfist-milights','Controller')
    self._bridge = None

  def isRunning(self):
    return self._running

  def stop(self, *args, **kwargs):
    self.logger.debug('Stopping thread')
    self._running = False

  def start(self, *args, **kwargs):

    if self._bridge_ip == None or self._bridge_port == None or self._bridge_version == None:
      self.logger.error('Bridge not configured properly')

    self._running = True


    self.logger.debug('Starting thread')
    super(Controller, self).start(*args, **kwargs)

  def addColorCommand(self, color, group):
    if self._bridge:
      g = self._bridge.get_group(group)
      cmd = g.color(color)

      self.addCommand(cmd)

  def addOnCommand(self, group):
    if self._bridge:
      g = self._bridge.get_group(group)
      cmd = g.on()

      self.addCommand(cmd)

  def addOffCommand(self, group):
    if self._bridge:
      g = self._bridge.get_group(group)
      cmd = g.off()

      self.addCommand(cmd)

  def brightness(self, brightness, group):
    if self._bridge:
      g = self._bridge.get_group(group)
      cmd = g.brightness(brightness)
      self.addCommand(cmd)

  def fadeIn(self, group):
    if self._bridge:
      g = self._bridge.get_group(group)

      for i in range(0,101):
        cmd = g.brightness(i)
        self.addCommand(cmd)

  def fadeOut(self, group):
    if self._bridge:
      g = self._bridge.get_group(group)

      for i in range(100,-1,-1):
        cmd = g.brightness(i)
        self.addCommand(cmd)

  def addCommand(self, command):
    self._queue.append(command)

  def initialize_bridge(self, bridge_ip, bridge_port, bridge_version, pause=100, repeat=1):

    if bridge_ip == '':
      bridge_ip = None

    if bridge_port == '':
      bridge_port = None

    if bridge_version == '':
      bridge_version = None

    self._bridge_ip = bridge_ip
    self._bridge_port = bridge_port
    self._bridge_version = bridge_version
    self._repeat = repeat
    self._pause = pause
    self._init_bridge = True

  def isBridgeAvailable(self):
    return not self._init_bridge == True

  def run(self):

    while self.isRunning():

      if self._bridge_ip == None or self._bridge_port == None or self._bridge_version == None:
        time.sleep(0.01)
        continue

      if self._init_bridge == True:
        self._bridge = WifiBridge(self._bridge_ip, self._bridge_port, self._bridge_version, self._pause, self._repeat)
        self._init_bridge = False

      if len(self._queue) > 0:
        cmd = self._queue.popleft()
        try:
          self._bridge._bridge.send(cmd)
        except socket.timeout:
          pass
      else:
        time.sleep(0.01)

    self.logger.info('Controller thread stopped')
