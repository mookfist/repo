from light import Lights, LightFadeThread
from utils import *

import xbmc, xbmcaddon
import time
import simplejson as json

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

  def _getPlayerType(self, data):
    if data['item']['type'] == 'episode':
      return 'tv'
    elif data['item']['type'] == 'movie':
      return 'movie'
    else:
      return None


  def _onPlay(self, data):
    playerType = self._getPlayerType(data)

    if playerType == None:
      log('Could not determine player type: %s' % data)
      return

    tvEnabled = __settings__.getSetting('tv_enabled')
    movieEnabled = __settings__.getSetting('movie_enabled')

    if (playerType == 'tv' and tvEnabled == 'true') or (playerType == 'movie' and movieEnabled == 'true'):

      for i in range(1,4):
        stepSpeed = getStepSpeed(i)
        if stepSpeed == None or self.lights.brightness(i) == None:
          self.lights.brightness(i, getMinBrightness(i))
        else:
          self.lights.fade(i, getMinBrightness(i), stepSpeed)


  def _onStop(self, data):
    playerType = self._getPlayerType(data)

    if playerType == None:
      log('Coult not determine player type: %s' % data, xbmc.LOGWARNING)
      return

    if (playerType == 'tv' and __settings__.getSetting('tv_enabled') == 'true') or (playerType == 'movie' and __settings__.getSetting('movie_enabled') == 'true'):

      for i in range(1,4):
        stepSpeed = getStepSpeed(i)
        if stepSpeed == None or self.lights.brightness(i) == None:
          self.lights.brightness(i, getMaxBrightness(i))
        else:
          self.lights.fade(i, getMaxBrightness(i), stepSpeed)


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


    for i in [0,1,2,3]:
      group = i + 1

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


if __name__ == "__main__":

  monitor = MyMonitor()
  monitor.onSettingsChanged()

  while not monitor.abortRequested():
    if monitor.waitForAbort(10):
      if monitor.lights:
        monitor.lights.stopFadeThread()
      break

