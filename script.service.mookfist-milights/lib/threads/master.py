import threading
import itertools
from collections import deque
import mookfist_lled_controller as lled
import mookfist_lled_controller.colors as lled_colors
from ..utils import Logger
import time

speeds = ['slow','medium','fast']
bridge_versions = [4,4,6]

class V4Thread(threading.Thread):
  def __init__(self, settings, *args, **kwargs):
    super(V4Thread, self).__init__(*args, **kwargs)
    self.logger = Logger('mookfist-milights', 'V4Thread')
    self.settings = settings

    self._cmd_queue = deque([])
    self._running = False
    self._bridge = lled.create_bridge(
      4,
      settings.getSetting('bridge_ip'),
      int(settings.getSetting('bridge_port')),
      int(settings.getSetting('pause')),
      int(settings.getSetting('repeat_count'))
    )

    self.groups = [GroupSettings(grp, self.settings) for grp in [0,1,2,3,4]]

  def add_command(self, cmd):
    self._cmd_queue.append(cmd)


  def reload(self):
    self.reset_queue()
    self._bridge = lled.create_bridge(
      4,
      self.settings.getSetting('bridge_ip'),
      int(self.settings.getSetting('bridge_port')),
      int(self.settings.getSetting('pause')),
      int(self.settings.getSetting('repeat_count'))
    )

    self.groups = [GroupSettings(grp, self.settings) for grp in [0,1,2,3,4]]



  def reset_queue(self):
    self._cmd_queue = deque([])


  def isRunning(self):
    return self._running


  def stop(self):
    self._running = False


  def get_last_brightness(self, group):
    return self.groups[group].brightness


  def get_last_color(self, group):
    return self.groups[group].color


  def run(self):
    self._running = True

    self.logger.debug('Thread starting')

    while self._running == True:
      if (len(self._cmd_queue) > 0):
        cmdName, group, args = self._cmd_queue.popleft()

        self.logger.debug('Command: %s - Group: %s - Args: %s' % (cmdName,group,args))

        if cmdName == 'white' or cmdName == 'on' or cmdName == 'off':
          getattr(self._bridge, cmdName)(group)
        elif cmdName == 'brightness' or cmdName == 'color':
          setattr(self.groups[group], cmdName, args[0])
          getattr(self._bridge, cmdName)(args[0], group)
      else:
        time.sleep(0.01)



class V6Thread(threading.Thread):
  def __init__(self, settings, *args, **kwargs):
    super(V6Thread, self).__init__(*args, **kwargs)
    self.logger = Logger('mookfist-milights', 'V6Thread')
    self._cmd_queue = deque([])
    self._running = False
    self._group_threads = (
      V6GroupThread(settings, 0),
      V6GroupThread(settings, 1),
      V6GroupThread(settings, 2),
      V6GroupThread(settings, 3),
      V6GroupThread(settings, 4)
    )


  def reload(self):

    self.reset_queue()

    for gt in self._group_threads:
      self.logger.debug('Stopping group thread: %s' % gt.group)
      gt.stop()

      while gt.isRunning() == True:
        time.sleep(0.01)

    self._group_threads = [
      V6GroupThread(settings, grp) for grp in [0,1,2,3,4]
    ]

    for gt in self._group_threads:
      self.logger.debug('Starting group thread: %s' % gt.group)
      gt.start()

      while gt.isRunning() == False:
        time.sleep(0.01)

      self.logger.debug('Group thread %s started' % gt.group)

  def get_last_brightness(self, group):
    return self._group_threads[group].group_settings.brightness


  def get_last_color(self, group):
    return self._group_threads[group].group_settings.color


  def isRunning(self):
    return self._running


  def add_command(self, cmd):
    grp = cmd[1]
    self._group_threads[grp].add_command(cmd)


  def reset_queue(self):
    self.logger.debug('Reset command queue')
    self._cmd_queue = deque([])


  def run(self):
    for grp in self._group_threads:
      grp.start()

    self._running = True

    while self._running == True:
      time.sleep(1)

    for grp in self._group_threads:
      grp.stop()


  def stop(self):
    self._running = False


class V6GroupThread(threading.Thread):
  def __init__(self, settings, group, *args, **kwargs):
    super(V6GroupThread, self).__init__(*args, **kwargs)
    self.logger = Logger('mookfist-milights', 'V6GroupThread-%s' % group)
    self.group = group
    self.settings = settings
    self._running = False
    self._bridge = None
    self._cmd_queue = deque([])
    self.group_settings = GroupSettings(group, settings)


  def isRunning(self):
    return self._running


  def reload(self):
    self.reset_queue()
    self._bridge = lled.create_bridge(
      6,
      self.settings.getSetting('bridge_ip'),
      int(self.settings.getSetting('bridge_port')),
      int(self.settings.getSetting('pause')),
      int(self.settings.getSetting('repeat_count'))
    )

  def add_command(self, cmd):
    self._cmd_queue.append(cmd)


  def reset_queue(self):
    self._cmd_queue = deque([])


  def run(self):
    self.reload()

    self._running = True

    while self._running == True:
      if (len(self._cmd_queue) > 0) :
        cmdName, group, args = self._cmd_queue.popleft()

        if cmdName == 'white' or cmdName == 'on' or cmdName == 'off':
          getattr(self._bridge, cmdName)(group)
        elif cmdName == 'brightness' or cmdName == 'color':
          setattr(self.group_settings, cmdName, args[0])
          getattr(self._bridge, cmdName)(args[0], group)
      else:
        time.sleep(0.01)


    self.logger.warning('Thread stopped')

  def stop(self):
    self._running = False


class GroupSettings():
  def __init__(self, group, settings):
    self.settings = settings
    self.group = group
    self.enabled = settings.getSetting('enable_group_%s' % self.group)
    self.enable_color_control = settings.getSetting('enable_color_control_group_%s' % self.group)
    self.start_color_value = settings.getSetting('group_%s_color_value' % self.group)
    self.start_brightness = int(settings.getSetting('group_%s_brightness' % self.group))
    self.color = self.start_color_value
    self.brightness = self.start_brightness
    self.on = True

    grp_steps_str = self.settings.getSetting('group_%s_fade_speed' % self.group)
    grp_steps = int(self.settings.getSetting('%s_speed_interval' % speeds[int(grp_steps_str)]))

    self.fade_speed = grp_steps


class MasterThread(threading.Thread):

  def __init__(self, settings, *args, **kwargs):
    super(MasterThread, self).__init__(*args, **kwargs)

    self.logger = Logger('mookfist-milights', 'MasterThread')

    self.settings = settings

    self._running = False
    self._reloading = True
    self._cmd_queue = deque([])
    self._bridge_thread = None
    self.groups = []


  def enabled_groups(self):

    return [
      grp for grp in (0,1,2,3,4)
      if self.settings.getSetting('enable_group_%s' % grp) == 'true'
    ]

    # return [grp.group for grp in self.groups if grp.enabled == True]


  def _group_arg(self, group=None):
    groups = []

    if group == None:
      groups = self.enabled_groups()
    elif isinstance(group, int):
      groups = (group,)
    elif isinstance(group, basestring):
      if group.isdigit():
        groups = (int(group),)
    else:
      groups = group

    self.logger.debug('_group_arg(): %s' % groups)
    return groups


  def reset_queue(self):
    self._cmd_queue = deque([])
    self._bridge_thread.reset_queue()


  def add_command(self, cmd, group, args=None):
    self._bridge_thread.add_command((cmd, group, args))


  def color(self, color, group=None):
    groups = self._group_arg(group)

    for group in groups:
      self.add_command('color', group, [color,])


  def color_rgb(self, r, g, b, group=None):
    self.color(color_from_rgb(r,g,b), group)


  def white(self, group=None):
    groups = self._group_arg(group)

    for group in groups:
      self.add_comand('white', group)


  def on(self, group=None):
    groups = self._group_arg(group)

    for group in groups:
      self.add_command('on', group)


  def off(self, group=None):
    groups = self._group_arg(group)

    for group in groups:
      self.add_command('off', group)


  def fade_out(self, group=None, restart=False):
    groups = self._group_arg(group)

    fade_cmds = []

    for group in groups:
      fade_group_cmds = []

      if restart == False:
        start_brightness = self._bridge_thread.get_last_brightness(group)
      else:
        start_brightness = self.groups[group].start_brightness

      self.logger.debug('Fading group %s from %s to %s' % (group, start_brightness, 0))

      for b in range(start_brightness, 0, -self.groups[group].fade_speed):
        fade_group_cmds.append({'b': b, 'g': group})

      fade_cmds.append(fade_group_cmds)

    for c in itertools.izip_longest(*fade_cmds):
      for idx in range(0, len(groups)):
        if c[idx] != None:
          self.brightness(c[idx]['b'], c[idx]['g'])


  def fade_in(self, group=None, restart=False):
    groups = self._group_arg(group)

    fade_cmds = []

    for group in groups:
      fade_group_cmds = []

      if restart == False:
        start_brightness = self._bridge_thread.get_last_brightness(group)
      else:
        start_brightness = 0

      self.logger.debug('Fading group %s from %s to %s' % (group, start_brightness, 100))

      for b in range(start_brightness, self.groups[group].start_brightness, self.groups[group].fade_speed):
        fade_group_cmds.append({'b': b, 'g': group})

      fade_cmds.append(fade_group_cmds)

    for c in itertools.izip_longest(*fade_cmds):
      for idx in range(0, len(groups)):
        if c[idx] != None:
          self.brightness(c[idx]['b'], c[idx]['g'])


  def brightness(self, b, group=None):
    groups = self._group_arg(group)

    for group in groups:
      self.groups[group].brightness = b
      self.add_command('brightness', group, [b,])


  def reload(self):

    self._reloading = True

    self.logger.debug('Reloading...')

    self.groups = [GroupSettings(grp, self.settings) for grp in [0,1,2,3,4]]

    if self._bridge_thread != None:
      self.logger.debug('Stopping bridge thread')

      self._bridge_thread.stop()

      while self._bridge_thread.isRunning() == True:
        time.sleep(0.01)

      self.logger.debug('Bridge thread confirmed stopped')

    bridge_ver = bridge_versions[int(self.settings.getSetting('bridge_version'))]

    if bridge_ver == 4:
      self._bridge_thread = V4Thread(self.settings)
    elif bridge_ver == 6:
      self._bridge_thread = V6Thread(self.settings)
    else:
      self.logger.error('Invalid bridge version: %s' % bridge_ver)

    self.logger.debug('Starting bridge thread')

    self._bridge_thread.start()

    while self._bridge_thread.isRunning() == False:
      time.sleep(0.01)

    self.on()
    time.sleep(0.10)
    self.off()
    time.sleep(0.10)
    self.on()
    time.sleep(0.10)

    self.logger.debug('Reloaded thread')
    self._reloading = False


  def run(self):
    self.reload()

    self._running = True

    while self._running == True:
      """
      if len(self._cmd_queue) > 0:
        cmd = self._cmd_queue.popleft()
        self._bridge_thread.add_command(cmd)
      else:
        time.sleep(0.01)
      """
      time.sleep(1)

    if self._bridge_thread:

      self.logger.debug('Stopping bridge thread')
      self._bridge_thread.stop()

      while self._bridge_thread.isRunning() == True:
        time.sleep(0.01)

      self.logger.warning('Bridge thread stopped')

    self.logger.warning('Master thread stopped')


  def stop(self):
    self._running = False

