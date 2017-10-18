import threading
import mookfist_lled_controller as lled
from collections import deque
import time
from .utils import Logger
import itertools

class MasterControllerThread(threading.Thread):

  def __init__(self, *args, **kwargs):
    super(MasterControllerThread, self).__init__(*args, **kwargs)

    self._group_states = {}

    self._bridge_ip = kwargs.get('bridge_ip', None)
    self._bridge_version = kwargs.get('bridge_version', None)
    self._bridge_port = kwargs.get('bridge_port', None)
    self._pause = kwargs.get('pause', 100)
    self._repeat = kwargs.get('repeat', 1)
    self._running = False
    self._bridge = None
    self._cmd_queue = deque([])
    self.logger = Logger('mookfist-milights', 'MasterControllerThread')
    self._is_bridge_initializing = False

    self._groups = {}

    grps = kwargs.get('groups', [])
    self.setGroups(grps)

  def setGroups(self, groups):
    for grp in groups:
      self._groups[grp.group] = grp

  def getEnabledGroups(self):
    return [grp for grp in self._groups if self._groups[grp].enabled is True]

  def enableGroup(self, group):
    self._groups[group].enabled = True

  def disableGroup(self, group):
    self._groups[group].enabled = False

  def isGroupEnabled(self, group):
    return self._groups[group].enabled

  def setGroupState(self, group, paramName, paramValue):

    if isinstance(group, basestring):
      groups = (group,)
    elif isinstance(group, int):
      groups = (group,)
    else:
      groups = group

    for grp in groups:
      setattr(self._groups[grp], paramName, paramValue)


  def isRunning(self):
    return self._running

  def brightness(self, brightness, group=None):
    self.addCommand('brightness', group, [brightness])

  def color(self, color, group=None):
    self.addCommand('color', group, [color])

  def color_rgb(self, r, g, b, group=None):
    self.addCommand('color_rgb', group, [r,g,b])

  def getGroupState(self, group, paramName):
    if group in self._group_states:
      if paramName in self._group_states[group]:
        return self._group_states[group][paramName]
      else:
        return None

  def fade(self, target, group=None, starting_brightness=None):

    if group is None:
      groups = [self._groups[grp] for grp in self._groups if self._groups[grp].enabled is True]
    else:
      groups = self._fix_groups(group)



    if isinstance(target, int):
      targetValue = target
      target = {}
      for group in groups:
        target[group.group] = targetValue

    fade_cmds = []


    for group in groups:


      group_fade_cmds = []

      if starting_brightness is None:
        starting_brightness = group.brightness

      if starting_brightness is None:
        starting_brightness = 0

      if starting_brightness > target[group.group]:
        steps = -group.fadeSteps
      else:
        steps = group.fadeSteps


      target_brightness = target[group.group]


      for b in range(starting_brightness, target_brightness, steps):
        group_fade_cmds.append({'b': b, 'g': group.group})

      fade_cmds.append(group_fade_cmds)

    cmds = itertools.izip_longest(*fade_cmds)

    for c in cmds:
      for idx in range(0, len(groups)):
        if c[idx] != None:
          self.brightness(c[idx]['b'], c[idx]['g'])



  def on(self, group=None):
    self.addCommand('on', group, [])

  def off(self, group=None):
    self.addCommand('off', group, [])

  def white(self, group=None):
    self.addCommand('white', group, [])

  def addCommand(self, cmdName, group, args):

    if group is None:
      group = self.getEnabledGroups()


    self._cmd_queue.append((cmdName, group, args))

  def initializeBridge(self, bridge_version, bridge_ip, bridge_port=None, pause=100, repeat=1):
    self._bridge = lled.create_bridge(bridge_version, bridge_ip, bridge_port, pause, repeat)
    self._is_bridge_initializing = False

  def setHost(self, bridge_host):
    self._bridge_ip = bridge_host

  def setPort(self, bridge_port):
    self._bridge_port = bridge_port

  def setVersion(self, bridge_version):
    self._bridge_version = bridge_version

  def setPause(self, pause):
    self._pause = pause

  def setRepeat(self, repeat):
    self._repeat

  def isBridgeInitializing(self):
    return self._is_bridge_initializing

  def reinitializeBridge(self):
    self._is_bridge_initializing = True

  def _fix_groups(self, group):
    try:
      if isinstance(group, basestring):
        if group == 'all':
          return (self._groups[group],)
        elif group.isdigit():
          return (self._groups[int(group)],)
      else:
        iter(group)

        ret = []

        for grp in group:
          if isinstance(grp, basestring):
            if grp == 'all':
              ret.append(self._groups['all'])
            elif grp.isdigit():
              ret.append(self._groups[int(grp)])

        return ret

    except TypeError:
      return (group,)

  def stop(self):
    self._running = False

  def run(self):

    self._running = True

    while self.isRunning():

      if self._is_bridge_initializing:
        self.initializeBridge(self._bridge_version, self._bridge_ip, self._bridge_port, self._pause, self._repeat)


      if len(self._cmd_queue) > 0:
        cmdName, group, args = self._cmd_queue.popleft()

        if cmdName == 'white' or cmdName == 'on' or cmdName == 'off':
          getattr(self._bridge, cmdName)(group)
          self.setGroupState(group, cmdName, True)
        elif cmdName == 'brightness' or cmdName == 'color':
          self.setGroupState(group, cmdName, args[0])
          getattr(self._bridge, cmdName)(args[0], group)

      else:
        time.sleep(0.01)

    self.logger.warning('Master controller thread stopped')
