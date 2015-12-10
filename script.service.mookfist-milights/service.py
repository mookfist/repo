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

  def log(self, msg, lvl=xbmc.LOGNOTICE):
    msg = "[milights] - [%s] %s" % (lvl, msg)
    xbmc.log(msg, level=lvl)

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
      self.log('Could not determine player type: %s' % data, xbmc.LOGWARNING)
      return

    tvEnabled = __settings__.getSetting('tv_enabled')
    movieEnabled = __settings__.getSetting('movie_enabled')

    self.log('TV Enabled: %s -- Movie Enabled: %s -- Player Type: %s' % (tvEnabled, movieEnabled, playerType))

    if (playerType == 'tv' and tvEnabled == 'true') or (playerType == 'movie' and movieEnabled == 'true'):
      self.log('-- Video has started playing')
      for i in range(1,4):
        if groupEnabled(i):
          stepSpeed = getStepSpeed(i)
          if stepSpeed == None:
            self.lights.brightness(getMinBrightness(i))
          else:
            self.lights.fade(getMinBrightness(i), stepSpeed, i)


  def _onStop(self, data):
    playerType = self._getPlayerType(data)

    if playerType == None:
      self.log('Coult not determine player type: %s' % data, xbmc.LOGWARNING)
      return

    if (playerType == 'tv' and __settings__.getSetting('tv_enabled') == 'true') or (playerType == 'movie' and __settings__.getSetting('movie_enabled') == 'true'):

      for i in range(1,4):
        if groupEnabled(i):
          stepSpeed = getStepSpeed(i)
          if stepSpeed == None:
            self.lights.brightness(100, i)
          else:
            self.lights.fade(getMaxBrightness(i), stepSpeed, i)


  def onSettingsChanged(self):
    if self.lights != None:
      self.lights.stopFadeThread()

    self.log(__settings__.getSetting('port'))
    host = __settings__.getSetting('light_host')
    port = __settings__.getSetting('light_port')

    if port == None:
      port = 8899
    else:
      try:
        port = int(port)
      except ValueError:
        port = 8899

    # @TODO This needs to change so different groups can have different bulb types
    bulbtype = getBulbType(1)
    wait_duration = int(__settings__.getSetting('command_delay'))

    self.lights = Lights(host, port, bulbtype, wait_duration)

    for i in [0,1,2,3]:
      group = i + 1

      if groupEnabled(group):
        self.log('setGroupLight()')
        self.lights.setGroupLight(group, maxBrightness=getMaxBrightness(group), minBrightness=getMinBrightness(group), color=getRgbColor(group))

        if doInitBrightness(group):
          self.log('doInitBrightness - %s - %s' % (getMaxBrightness(group), group))
          self.lights.brightness(group, getMaxBrightness(group))

        if doInitColor(group):
          self.log('doInitColor')
          self.lights.color(group, getRgbColor(group))
      else:
        self.lights.removeGroupLight(group)


  def onNotification(self, sender, method, data):

    self.log("SENDER: %s --- METHOD %s --- DATA %s" % (sender, method, data))

    data = json.loads(data)

    if str(sender) == "xbmc" and str(method) == "Player.OnPlay":
      self.log("XBMC Player starts")
      self._onPlay(data)
    elif str(sender) == "xbmc" and str(method) == "Player.OnStop":
      self.log("XBMC Player ends")
      self._onStop(data)


if __name__ == "__main__":

  monitor = MyMonitor()
  monitor.onSettingsChanged()

  while not monitor.abortRequested():
    if monitor.waitForAbort(10):
      if monitor.lights:
        monitor.lights.stopFadeThread()
      break

