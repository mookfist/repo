import threading
from utils import Logger
from mookfist_lled_controller import WifiBridge
from collections import deque
import socket
import time
import itertools

class Controller(threading.Thread):

  def __init__(self, *args, **kwargs):
    super(Controller, self).__init__()

    self._settings = kwargs.get('settings', None)
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

    self._group_states = {}

    for grp in (1,2,3,4):

      if self._settings.getSetting('enable_group%s' % grp) == 'true':

        color = self._settings.getSetting('group%s_color_value' % grp)

        r = int(color[2:4], 16)
        g = int(color[4:6], 16)
        b = int(color[6:8], 16)

        self._group_states[grp] = {
            'brightness': int(self._settings.getSetting('group%s_brightness' % grp)),
            'color': {
              'r': r,
              'b': b,
              'g': g
            },
            'on': True,
            'off': False
        }
      else:
        self._group_states[grp] = {
            'brightness': 0,
            'color': {
              'r': 0,
              'g': 0,
              'b': 0
            },
            'on': False,
            'off': True
        }


  def isRunning(self):
    return self._running

  def stop(self, *args, **kwargs):
    self.logger.debug('Stopping thread')
    self._running = False

  def reset_queue(self):
    self._queue.clear()

  def start(self, *args, **kwargs):

    if self._bridge_ip == None or self._bridge_port == None or self._bridge_version == None:
      self.logger.error('Bridge not configured properly')

    self._running = True


    self.logger.debug('Starting thread')
    super(Controller, self).start(*args, **kwargs)

  def fade_out(self, groups):

    speeds = ['slow','medium','fast']

    fade_cmds = []

    for grp in groups:
      grp_fade_cmds = []
      interval_str = self._settings.getSetting('group%s_fade_speed' % grp)
      interval = int(self._settings.getSetting('%s_speed_interval' % speeds[int(interval_str)]))
      starting_brightness = self._group_states[grp]['brightness']
      ending_brightness = -1

      self.logger.debug('Fading out group %s at speed %s (%s steps)' % (grp, interval_str, interval))

      fade_cmds.append(range(starting_brightness, ending_brightness, -interval))

    merged_cmds = itertools.izip_longest(*fade_cmds)

    for cmds in merged_cmds:
      grp_idx = 0
      for brightness in cmds:
        grp = int(groups[grp_idx])

        if brightness != None:
          self.brightness(brightness, (grp,))
        grp_idx = grp_idx + 1

  def fade_in(self, groups):

    speeds = ['slow','medium','fast']

    fade_cmds = []

    for grp in groups:
      grp_fade_cmds = []
      interval_str = self._settings.getSetting('group%s_fade_speed' % grp)
      interval = int(self._settings.getSetting('%s_speed_interval' % speeds[int(interval_str)]))
      starting_brightness = self._group_states[grp]['brightness']
      ending_brightness = int(self._settings.getSetting('group%s_brightness' % grp))

      self.logger.debug('Fading in group %s at speed %s (%s steps)' % (grp, interval_str, interval))

      fade_cmds.append(range(starting_brightness, ending_brightness, interval))

    merged_cmds = itertools.izip_longest(*fade_cmds)

    for cmds in merged_cmds:
      grp_idx = 0
      for brightness in cmds:
        grp = int(groups[grp_idx])

        if brightness != None:
          self.brightness(brightness, (grp,))
        grp_idx = grp_idx + 1


  def color_rgb(self, r, g, b, group):
    if self._bridge:
      for grp in group:
        args = [int(r),int(g),int(b),int(grp)]
        cmd  = self._bridge.color_rgb

        self.addCommand((cmd,args))

  def color(self, color, group):
    if self._bridge:
      for g in group:
        args = [color, g]
        cmd  = self._bridge.color

        self.addCommand((cmd,args))
  def white(self, groups):
    if self._bridge:
      for g in groups:
        args = [g]
        cmd  = self._bridge.white

        self.addCommand((cmd,args))

  def on(self, group):
    if self._bridge:
      for g in group:
        args = [g]
        cmd  = self._bridge.on

        self.addCommand((cmd,args))

  def off(self, group):
    if self._bridge:
      for g in group:
        args = [g]
        cmd = self._bridge.off

        self.addCommand((cmd,args))

  def brightness(self, brightness, group):
    if self._bridge:
      for g in group:
        args = [brightness, g]
        cmd  = self._bridge.brightness

        self.addCommand((cmd, args))


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
        cmd, args = self._queue.popleft()
        try:
          self.logger.debug('cmd: %s -- args: %s' % (cmd.__name__, args))

          if cmd.__name__ == 'brightness':
            self._group_states[args[1]]['brightness'] = args[0]
          elif cmd.__name__ == 'color_rgb':
            self._group_states[args[3]]['color'] = {
                'r': args[0],
                'b': args[1],
                'g': args[2]
            }
          elif cmd.__name__ == 'color':
            self._group_states[args[1]]['color'] = args[0]
          elif cmd.__name__ == 'white':
            self._group_states[args[0]]['color'] = {
                'r': 255,
                'g': 255,
                'b': 255
            }
          elif cmd.__name__ == 'off':
            self._group_states[args[0]]['off'] = True
            self._group_states[args[0]]['on'] = False
          elif cmd.__name__ == 'on':
            self._group_states[args[0]]['off'] = False
            self._group_states[args[0]]['on']  = True

          cmd(*args)
        except socket.timeout:
          pass
      else:
        time.sleep(0.01)

    self.logger.info('Controller thread stopped')
