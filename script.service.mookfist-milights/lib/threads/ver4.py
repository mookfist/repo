import threading
import mookfist_lled_controller as lled
from collections import deque
import time
from ..utils import Logger
import itertools

class Ver4Thread(threading.Thread):

  def __init__(self, *args, **kwargs):
    super(Ver4Thread, self).__init__(*args, **kwargs)

    self._bridge_ip = None
    self._bridge_port = None
    self._bridge_version = 4
    self._pause = None
    self._repeat = None
    self._bridge = None
    self._is_initializing = False
    self._is_running = False
    self._kodi_settings = kwargs.get('settings')

    self.logger = Logger('mookfist-milights', 'ThreadV4')

    self._groups = {}

  def brightness(self, brightness, groups):
    self.addCommand('brightness', group, [brightness])

  def color(self, color, group):
    self.addCommand('color', groups, [color])

  def color_rgb(self, r, g, b, groups):
    self.addCommand('color_rgb', groups, [r,g,b])

  def getGroupState(self, group, paramName):

    if group not in self._groups:
      self._groups[group] = {}

    if paramName in self._groups[group]:
      return self._groups[group]

    return None

  def fade(self, target, groups, starting_brightness=None):

    fade_cmds = []

    for group in groups:

      group_fade_cmds = []

      if starting_brightness is None:
        starting_brightness = self.getGroupState(group, 'brightness')

      if starting_brightness is None:
        starting_brightness = 0

      if starting_brightness > target:




  def reload(self):

    settings = self._kodi_settings

    self._is_initializing = True
    self._bridge_ip = settings.getSetting('bridge_ip')
    self._bridge_port = int(settings.getSetting('bridge_port'))
    self._pause = int(settings.getSetting('pause'))
    self._repeat = int(settings.getSetting('repeat'))

    self._bridge = lled.create_bridge(4, self._bridge_ip, self._bridge_port, self._pause, self._repeat)

    self._is_initializing = False

  def stop(self):
    self._is_running = False

  def isRunning(self):
    return self._is_running

  def run(self):
    self._is_running = True

    if not self._bridge:
      self.reload()

    while self._is_running:

      if len(self._cmd_queue) > 0:
        cmdName, group, args = self._cmd_queue.popleft()

        if cmdName == 'white' or cmdName == 'on' or cmdName == 'off':
          getattr(self._bridge, cmdName)(group)
          self.setGroupState(group, cmdName, True)
        elif cmdName == 'brightness' or cmdName == 'color':
          getattr(self._bridge, cmdName)(args[0], group)
          self.setGroupState(group, cmdName, args[0])
      else:
        time.sleep(0.01)

    self.logger.warning('Thread stopped')




