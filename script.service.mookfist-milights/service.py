import xbmc, xbmcaddon
import time, math
import simplejson as json
import threading

from lib.controller import Controller
from lib.utils import Logger
from lib.utils import initialize_logger

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

    for grp in [1,2,3,4]:
      if __settings__.getSetting('enable_group%s' % grp) == 'true':
        self._enabled_groups.append(grp)

  def dispatch_bridge_command(self, method, data):

    self.logger.debug('Dispatching bridge command: %s - %s' % (method, data))

    if method == 'white':
      self.controller_thread.white(data['groups'])
    elif method == 'fade-out':
      self.controller_thread.fade_out(data['groups'])
    elif method == 'fade-in':
      self.controller_thread.fade_in(data['groups'])
    elif method == 'brightness':
      self.controller_thread.brightness(data['brightness'], data['groups'])

    return

    if method == 'on':
      self.controller_thread.on(int(data['group']))
    elif method == 'off':
      self.controller_thread.off(int(data['group']))
    elif method == 'fadein':
      self.controller_thread.fadeIn(int(data['group']))
    elif method == 'fadeout':
      self.controller_thread.fadeOut(int(data['group']))
    elif method == 'fade_outin':
      self.controller_thread.fadeOut(data['group'])
      self.controller_thread.fadeIn(data['group'])
    elif method == 'brightness':
      self.controller_thread.brightness(data['brightness'], int(data['group']))
    elif method == 'fade-out':
      self.controller_thread.fade_out(data['group'])

  def dispatch_xbmc_command(self, method, data):
    if method == 'Player.OnPlay':
      if data['item']['type'] == 'movie' and __settings__.getSetting('autoplay_movie') == 'true':
        self.controller_thread.reset_queue()
        self.controller_thread.fade_out(self._enabled_groups)
      elif data['item']['type'] == 'episode' and __settings__.getSetting('autoplay_tv') == 'true':
        self.controller_thread.reset_queue()
        self.controller_thread.fade_out(self._enabled_groups)
    elif method == 'Player.OnStop':
      if data['item']['type'] == 'movie' and __settings__.getSetting('autoplay_movie') == 'true':
        self.controller_thread.reset_queue()
        self.controller_thread.fade_in(self._enabled_groups)
      elif data['item']['type'] == 'episode' and __settings__.getSetting('autoplay_tv') == 'true':
        self.controller_thread.reset_queue()
        self.controller_thread.fade_in(self._enabled_groups)



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

    self.controller_thread.initialize_bridge(
        bridge_ip=bridge_ip,
        bridge_port=bridge_port,
        bridge_version=bridge_version,
        repeat=repeat,
        pause=pause
    )

    while self.controller_thread.isBridgeAvailable() == False:
      time.sleep(0.01)

    groups = []

    for x in range(1,5):

      brightness = int(__settings__.getSetting('group%s_brightness' % x))
      color = __settings__.getSetting('group%s_color_value' % x)

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

          print color
          color = ''.join(color)
          __settings__.setSetting('group%s_color_value' % x, color)
          return


      if __settings__.getSetting('enable_group%s' % x) == 'true':
        groups.append(x)



    for x in range(0,3):
      self.controller_thread.on(groups)
      time.sleep(0.2)
      self.controller_thread.off(groups)
      time.sleep(0.2)

    for g in groups:

      brightness = int(__settings__.getSetting('group%s_brightness' % g))
      color = __settings__.getSetting('group%s_color_value' % g)

      red = int(color[2:4], 16)
      green = int(color[4:6], 16)
      blue = int(color[6:8], 16)

      self.controller_thread.on([g])
      self.controller_thread.color_rgb(red,green,blue,[g])
      self.controller_thread.brightness(brightness,[g])


"""
class MyMonitor(xbmc.Monitor):

  def __init__(self):
    xbmc.Monitor.__init__(self)
    self.lights = None
    self.paused = False

  def _getPlayerType(self, data):
    if data['item']['type'] == 'episode':
      return 'tv'
    elif data['item']['type'] == 'movie':
      return 'movie'
    else:
      return None


  def _onPlay(self, data):
    playerType = self._getPlayerType(data)

    useCustomPauseSpeed = __settings__.getSetting('global_enable_pause_speed')

    if self.paused == False:
      useCustomPauseSpeed = False

    self.paused = False

    if playerType == None:
      log('Could not determine player type: %s' % data)
      return

    tvEnabled = __settings__.getSetting('tv_enabled')
    movieEnabled = __settings__.getSetting('movie_enabled')

    if (playerType == 'tv' and tvEnabled == 'true') or (playerType == 'movie' and movieEnabled == 'true'):

      for i in range(1,5):
        if (useCustomPauseSpeed == True or useCustomPauseSpeed == "true"):
          stepSpeed = getPauseStepSpeed(i)
        else:
          stepSpeed = getMainStepSpeed(i)

        if stepSpeed == None or self.lights.brightness(i) == None:
          self.lights.brightness(i, getMinBrightness(i))
        else:
          self.lights.fade(i, getMinBrightness(i), stepSpeed)


  def _onStop(self, data):
    playerType = self._getPlayerType(data)
    self.paused = False

    if playerType == None:
      log('Coult not determine player type: %s' % data, xbmc.LOGWARNING)
      return

    if (playerType == 'tv' and __settings__.getSetting('tv_enabled') == 'true') or (playerType == 'movie' and __settings__.getSetting('movie_enabled') == 'true'):

      for i in range(1,5):
        stepSpeed = getMainStepSpeed(i)
        if stepSpeed == None or self.lights.brightness(i) == None:
          self.lights.brightness(i, getMaxBrightness(i))
        else:
          self.lights.fade(i, getMaxBrightness(i), stepSpeed)


  ef _onPause(self, data):

    self.paused = True

    useCustomPauseSpeed = __settings__.getSetting('global_enable_pause_speed')
    pauseDelay          = int(__settings__.getSetting('global_pause_delay'))

    log('_onPause() - pause speed enabled: %s' % useCustomPauseSpeed)

    for i in range(1,5):
      # we need to spread out pauseDelay because otherwise
      # it seems not all groups will be affected
      if useCustomPauseSpeed == True or useCustomPauseSpeed == "true":
        stepSpeed = getPauseStepSpeed(i)
      else:
        stepSpeed = getMainStepSpeed(i)

      if stepSpeed == None or self.lights.brightness(i) == None:

        if pauseDelay > 0:
          t = threading.Timer(pauseDelay, self.lights.brightness, [i, getMaxBrightness(i)], {})
          t.start()
        else:
          self.lights.brightness(i, getMaxBrightness(i))
      else:
        if pauseDelay > 0:
          t = threading.Timer(pauseDelay, self.lights.fade, [i, getMaxBrightness(i), stepSpeed], {})
          t.start()
        else:
          self.lights.fade(i, getMaxBrightness(i), stepSpeed)

      # we need to spread out pauseDelay because otherwise
      # it seems not all groups will be affected
      pauseDelay = pauseDelay + 0.25



  def onSettingsChanged(self):

    host = __settings__.getSetting('light_host')
    port = __settings__.getSetting('light_port')
    # @TODO This needs to change so different groups can have different bulb types
    bulbtype = getBulbType(1)
    wait_duration = int(__settings__.getSetting('command_delay'))

    try:
      port = int(port)
    except ValueError:
      port = 8899

    if self.lights == None:
      self.lights = Lights(host, port, bulbtype, wait_duration)
    else:
      self.lights.stopFadeThread()
      self.lights.setHost(host, port)
      self.lights.setBulbType(bulbtype)
      self.lights.setWaitDuration(wait_duration)


    for group in range(1,5):

      if groupEnabled(group):
        self.lights.setGroupLight(group, maxBrightness=getMaxBrightness(group), minBrightness=getMinBrightness(group), color=getRgbColor(group))

        if doInitBrightness(group):
          self.lights.brightness(group, getMaxBrightness(group))

        if doInitColor(group):
          self.lights.color(group, getRgbColor(group))
      else:
        self.lights.removeGroupLight(group)

  def onFadeOut(self, data):

    log('data: %s' % data)

    group = data['group']
    if group == 'all':
      groups = range(1, 5)
    else:
      groups = [group]

    if data['brightness'] > -1:
      brightness = data['brightness']
    else:
      brightness = getMinBrightness(group)

    for group in groups:
      self.lights.fade(group, brightness, getMainStepSpeed(group))

  def onFadeIn(self, data):
    group = data['group']
    if group == 'all':
      groups = range(1,5)
    else:
      groups[group]

    for group in groups:
      self.lights.fade(group, getMaxBrightness(group), getMainStepSpeed(group))






  def onNotification(self, sender, method, data):

    log("SENDER: %s --- METHOD %s --- DATA %s" % (sender, method, data))

    data = json.loads(data)

    if str(sender) == 'mookfist-milights':
        if str(method) == 'Other.fade_out':
          self.onFadeOut(data)
        elif str(method) == 'Other.fade_in':
          self.onFadeIn(data)

    elif str(sender) == "xbmc" and str(method) == "Player.OnPlay":
      self._onPlay(data)
    elif str(sender) == "xbmc" and str(method) == "Player.OnStop":
      self._onStop(data)
    elif str(sender) == "xbmc" and str(method) == "Player.OnPause":
      self._onPause(data)
"""

if __name__ == "__main__":

  initialize_logger()

  bridge_ip = __settings__.getSetting('bridge_ip')
  bridge_port = __settings__.getSetting('bridge_port')
  bridge_version = __settings__.getSetting('bridge_version')
  repeat = int(__settings__.getSetting('repeat_count'))
  pause = int(__settings__.getSetting('pause'))

  if bridge_port != None and bridge_port != '':
    bridge_port = int(bridge_port)

  if bridge_version != None and bridge_version != '':
    bridge_version = int(bridge_version)

  if bridge_version == 0:
    bridge_version = 4
  elif bridge_version == 1:
    bridge_version = 5
  elif bridge_version == 2:
    bridge_version = 6
  else:
    bridge_version = None


  controller = Controller(settings=__settings__)
  monitor = ServiceMonitor(controller)

  controller.initialize_bridge(
      bridge_ip=bridge_ip,
      bridge_port=bridge_port,
      bridge_version=bridge_version,
      repeat=repeat,
      pause=pause
  )
  controller.start()

  monitor.onSettingsChanged()

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
