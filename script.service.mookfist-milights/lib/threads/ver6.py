import threading
import mookfist_lled_controllre as lled
from collections import deque
import time
from .utils import Logger

class GroupThread(threading.Thread):

  def __init__(self, *args, **kwargs):
    super(Groupthread, self).__init__(*args, **kwargs)

    self._bridge_ip = kwargs.get('bridge_ip', None)
    self._bridge_version = kwargs.get('bridge_version', None)
    self._bridge_port = kwargs.get('bridge_port', None)
    self._pause = kwargs.get('pause', 100)
    self._repeat = kwargs.get('repeat', 1)
    self._running = False
    self._bridge = None
    self._group = kwargs.get('group', 0)
    self._cmd_queue = deque([])
    self._is_initializing = False

    self.enabled = False
    self.logger = Logger('mookfist-milights', 'GroupThread%s' % self._group)

  def fade(self, bFrom, bTo, steps=1):

    if bFrom > bTo:
      steps = -steps

    for b in range(bFrom, bTo, steps):
      self.brightness(b)

  def brightness(self, b):
    self.addCommand('brightness', [b])

  def on(self):
    self.addCommand('on')

  def off(self):
    self.addCommand('off')

  def white(self):
    self.addCommand('white')

  def color(self, color):
    self.addCommand('color', [color])

  def color_rgb(self, r, g, b):
    self.addCommand('color_rgb', [r,g,b])

  def isRunning(self):
    return self._running

  def addCommand(cmdName, args):
    self._cmd_queue.append((cmdName, args))

  def initialize(self):
    self._is_initializing = True
    self._bridge = lled.create_bridge(self._bridge_version, self._bridge_ip, self._bridge_port, self._pause, self._repeat)
    self._is_initializing = False


  def initialize(self):
    pass

  def stop(self):
    self._running = False

  def run(self):
    self._running = True

    if not self._bridge:
      self.initialize()

    while self.isRunning() == True:
      if self._is_initializing == True:
        time.sleep(0.01)
        return

      if len(self._cmd_queue) > 0:
        cmdName, args = self._cmd_queue.popleft()

        if cmdName == 'white' or cmdName == 'on' or cmdName == 'off':
          getattr(self._bridge, cmdName)(self._group)
        else:
          getattr(self._bridge, cmdName)(args[0], self._group)
      else:
        time.sleep(0.01)


