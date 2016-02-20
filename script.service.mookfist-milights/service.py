from light import Lights, LightFadeThread
from utils import *

import xbmc, xbmcaddon
import time
import simplejson as json
import threading

__scriptname__ = "Mookfist Milights"
__author__     = "Mookfist"
__url__        = "https://github.com/mookfist/repo"
__settings__   = xbmcaddon.Addon(id='script.service.mookfist-milights')
__version__    = __settings__.getAddonInfo('version')
__language__   = __settings__.getLocalizedString


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


  def _onPause(self, data):

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


  def onNotification(self, sender, method, data):

    # log("SENDER: %s --- METHOD %s --- DATA %s" % (sender, method, data))

    data = json.loads(data)

    if str(sender) == "xbmc" and str(method) == "Player.OnPlay":
      self._onPlay(data)
    elif str(sender) == "xbmc" and str(method) == "Player.OnStop":
      self._onStop(data)
    elif str(sender) == "xbmc" and str(method) == "Player.OnPause":
      self._onPause(data)


if __name__ == "__main__":

  monitor = MyMonitor()
  monitor.onSettingsChanged()

  while not monitor.abortRequested():
    if monitor.waitForAbort(10):
      if monitor.lights:
        monitor.lights.stopFadeThread()
      break

