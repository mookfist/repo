import xbmc, xbmcaddon
import time, math
import simplejson as json

from lib.utils import Logger
from lib.utils import initialize_logger
from lib.masterController import MasterControllerThread
from lib.group import Group

from mookfist_lled_controller.colors import color_from_html

__scriptname__ = "Mookfist Milights"
__author__     = "Mookfist"
__url__        = "https://github.com/mookfist/repo"
__settings__   = xbmcaddon.Addon(id='script.service.mookfist-milights')
__version__    = __settings__.getAddonInfo('version')


class ServiceMonitor(xbmc.Monitor):

  def __init__(self, controller_thread):
    xbmc.Monitor.__init__(self)
    self.logger = Logger('mookfist-milights', 'service')
    self.controller_thread = controller_thread

    self._enabled_groups = []

    self.pay_attention = False

    if __settings__.getSetting('enable_group_all') == 'true':
      self._enabled_groups.append('all')
    else:
      for grp in [1,2,3,4]:
        if __settings__.getSetting('enable_group_%s' % grp) == 'true':
          self._enabled_groups.append(grp)

  def dispatch_bridge_command(self, method, data):

    self.logger.debug('Dispatching bridge command: %s - %s' % (method, data))

    if method == 'white':
      self.controller_thread.white(data['groups'])
    elif method == 'fade-out':
      self.controller_thread.fade(0, data['groups'])
    elif method == 'fade-in':
      self.controller_thread.fade(100, data['groups'])
    elif method == 'fade-outin':
      self.controller_thread.fade(0, data['groups'], 100)
      self.controller_thread.fade(100, data['groups'], 0)
    elif method == 'brightness':
      self.controller_thread.brightness(data['brightness'], data['groups'])
    elif method == 'color-rgb':
      self.controller_thread.color_rgb(data['r'], data['b'], data['g'], data['groups'])
    elif method == 'pay-attention':
      self.pay_attention = True

  def dispatch_xbmc_command(self, method, data):
    if method == 'Player.OnPlay':

      if ((self.pay_attention == True)
      or (data['item']['type'] == 'movie' and __settings__.getSetting('autoplay_movie') == 'true')
      or (data['item']['type'] == 'episode' and __settings__.getSetting('autoplay_tv') == 'true')):
        self.controller_thread.reset_queue()
        self.controller_thread.fade_out(self._enabled_groups)
        self.pay_attention = True
    elif method == 'Player.OnStop':
      if ((self.pay_attention == True)
      or (data['item']['type'] == 'movie' and __settings__.getSetting('autoplay_movie') == 'true')
      or (data['item']['type'] == 'episode' and __settings__.getSetting('autplay_tv') == 'true')):
        self.controller_thread.reset_queue()
        self.controller_thread.fade_in(self._enabled_groups)
        self.pay_attention = False


  def onNotification(self, sender, method, data):
    self.logger.debug("SENDER: %s --- METHOD %s --- DATA %s" % (sender, method, data))
    if sender == 'mookfist-milights':
      self.dispatch_bridge_command(method.replace('Other.',''), json.loads(data))
    elif sender == 'xbmc':
      self.dispatch_xbmc_command(method, json.loads(data))


  def onSettingsChanged(self):

    self.logger.debug('Plugin settings have changed')

    self.controller_thread.reset_queue()

    bridge_ip = __settings__.getSetting('bridge_ip')
    bridge_port = int(__settings__.getSetting('bridge_port'))
    bridge_version = int(__settings__.getSetting('bridge_version'))
    repeat = int(__settings__.getSetting('repeat_count'))
    pause = int(__settings__.getSetting('pause'))

    if bridge_version == 0:
      bridge_version = 4
    elif bridge_version == 1:
      bridge_version = 5
    elif bridge_version == 2:
      bridge_version = 6

    self.controller_thread.setVersion(bridge_version)
    self.controller_thread.setHost(bridge_ip)
    self.controller_thread.setPort(bridge_port)
    self.controller_thread.setPause(pause)
    self.controller_thread.setRepeat(repeat)

    self.controller_thread.reinitializeBridge()

    while self.controller_thread.isBridgeInitializing() == True:
      time.sleep(0.01)

    groups = []

    for x in ['all', 1, 2, 3, 4]:

      brightness = __settings__.getSetting('group_%s_brightness' % x)
      color = __settings__.getSetting('group_%s_color_value' % x)

      if brightness != '':
        brightness = int(brightness)

      if color != '':

        color_brightness = int(color[0:2],16)
        color_brightness = int(math.floor((float(color_brightness) / 255.0) * 100.0))

        self.logger.debug('CB: %s - B: %s' % (color_brightness, brightness))
        if color_brightness != brightness:

          new_brightness = hex(int(math.ceil((brightness / 100.0) * 255.0)))
          color = list(color)
          color[0] = new_brightness[2]
          if len(new_brightness) == 4:
            color[1] = new_brightness[3]
          else:
            color[1] = '0'

          color = ''.join(color)
          __settings__.setSetting('group_%s_color_value' % x, color)
          return


      if __settings__.getSetting('enable_group_%s' % x) == 'true':
        groups.append(x)

    if len(groups) is 1:
      groups = (groups[0],)

    for x in range(0,3):
      self.controller_thread.on(groups)
      time.sleep(0.2)
      self.controller_thread.off(groups)
      time.sleep(0.2)

    for g in groups:
      self.controller_thread.on([g,])

      brightness = __settings__.getSetting('group_%s_brightness' % g)

      if brightness != None and brightness != '':
        try:
          brightness = int(brightness)
          self.controller_thread.brightness(brightness,[g,])
        except ValueError:
          self.logger.warning('The brightness level for group %s could not be converted into an int. Current value: \'%s\'' % (g, brightness))

      color = __settings__.getSetting('group_%s_color_value' % g)
      if color != None and color != '':
        try:
          red = int(color[2:4], 16)
          green = int(color[4:6], 16)
          blue = int(color[6:8], 16)

          self.controller_thread.color_rgb(red,green,blue,[g])
        except ValueError:
          self.logger.warning('There was an error converting the color for group %s. Current value: \'%s\'' % (g, color))


def setup_groups():
  groups = []

  speeds = ['slow','medium','fast']

  for grp in ['all', 1, 2, 3, 4]:

    grpobj = Group(grp)

    grp_steps_str = __settings__.getSetting('group_%s_fade_speed' % grp)
    grp_steps = int(__settings__.getSetting('%s_speed_interval' % speeds[int(grp_steps_str)]))

    grpobj.fadeSteps = grp_steps
    grpobj.enabled = __settings__.getSetting('enable_group_%s' % grp) == 'true'
    grpobj.color_control = __settings__.getSetting('enable_color_control_group_%s' % grp) == 'true'
    grpobj.brightness = int(__settings__.getSetting('group_%s_brightness' % grp))

    colorhex = __settings__.getSetting('group_%s_color_value' % grp)

    if colorhex:
      grpobj.color = color_from_html(colorhex[0:6])

    groups.append(grpobj)

  return groups


if __name__ == "__main__":

  initialize_logger()
  controller = MasterControllerThread()
  monitor    = ServiceMonitor(controller)

  bridge_ip = __settings__.getSetting('bridge_ip')
  bridge_port = __settings__.getSetting('bridge_port')
  bridge_version = __settings__.getSetting('bridge_version')
  repeat = int(__settings__.getSetting('repeat_count'))
  pause = int(__settings__.getSetting('pause'))

  if bridge_port != '' and bridge_ip != '' and bridge_version != '':
    bridge_port = int(bridge_port)
    bridge_version = int(bridge_version)

    if bridge_version == 0:
      bridge_version = 4
    elif bridge_version == 1:
      bridge_version = 5
    elif bridge_version == 2:
      bridge_version = 6

    controller.setHost(bridge_ip)
    controller.setPort(bridge_port)
    controller.setVersion(bridge_version)
    controller.setPause(pause)
    controller.setRepeat(repeat)
    controller.setGroups(setup_groups())

    controller.start()
    controller.reinitializeBridge()

    while controller.isBridgeInitializing() != False:
      time.sleep(0.01)

    for i in range(0,3):
      controller.off()
      time.sleep(0.3)
      controller.on()

  while not monitor.abortRequested():
    if monitor.waitForAbort(10):
      controller.stop()

"""
  monitor = MyMonitor()
  monitor.onSettingsChanged()

  while not monitor.abortRequested():
    if monitor.waitForAbort(10):
      if monitor.lights:
        monitor.lights.stopFadeThread()
      break
"""
