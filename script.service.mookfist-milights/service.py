from light import Lights
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

  def __init__(self, lights):
    xbmc.Monitor.__init__(self)
    self.lights = lights


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

    if playerType == 'tv' and tvEnabled == 'true':
      self.log('TV show has started playing, time to fade out the lights')
#      self.lights.fadeOff()
    elif playerType == 'movie' and movieEnabled == 'true':
      self.log('Movie has started playing, time to fade out the lights')
      self.lights.fadeOff()


  def _onStop(self, data):
    playerType = self._getPlayerType(data)

    if playerType == None:
      self.log('Coult not determine player type: %s' % data, xbmc.LOGWARNING)
      return

    if playerType == 'tv' and __settings__.getSetting('tv_enabled') == 'true':
      self.log('TV show has stopped playing, time to fade on the lights')
#      self.lights.fadeOn()
    elif playerType == 'movie' and __settings__.getSetting('movie_enabled') == 'true':
      self.log('Movie show has stopped playing, time to fade on the lights')
#      self.lights.fadeOn()


  def onNotification(self, sender, method, data):

    self.log("SENDER: %s --- METHOD %s --- DATA %s" % (sender, method, data))

    data = json.loads(data)

    if str(sender) == "xbmc" and str(method) == "Player.OnPlay":
      self.log("XBMC Player starts")
      self._onPlay(data)
    elif str(sender) == "xbmc" and str(method) == "Player.OnStop":
      self.log("XBMC Player ends")
      self._onStop(data)

def groupEnabled(group):
  return __settings__.getSetting('enable_group%s' % group) == 'true'

def doInitBrightness(group):
  if __settings__.getSetting('global_set_brightness_at_start') == 'true':
    return True

def doInitColor(group):
  if __settings__.getSetting('global_enable_color') == 'true':
    return True

def getRedColor(group):
  return __settings__.getSetting('global_red_value')

def getGreenColor(group):
  return __settings__.getSetting('global_green_value')

def getBlueColor(group):
  return __settings__.getSetting('global_blue_value')

def getMaxBrightness(group):
  return int(__settings__.getSetting('global_max_brightness'))

def getMinBrightness(group):
  return int(__settings__.getSetting('global_min_brightness'))

def getBulbType(group):
  typeNumber = int(__settings__.getSetting('global_bulb_type'))

  if typeNumber == 0:
    return 'white'
  elif typeNumber == 1:
    return 'rgbw'
  else:
    return 'rgb'

def log(msg):
  xbmc.log('[mookfist-milights] %s' % msg)


if __name__ == "__main__":

  host = __settings__.getSetting('light_host')
  port = int(__settings__.getSetting('light_port'))
  bulbType = getBulbType(1)

  log('Bulb Type: %s' % bulbType)

  l = Lights(host, port, bulbType)

  monitor = MyMonitor(lights=l)

  for i in range(1,4):
    if groupEnabled(i) == False:
      continue

    l.on(i)

    if doInitBrightness(i):
      targetBrightness = getMaxBrightness(i)

      log('Setting initial brightness to %s for group %s' % (targetBrightness, i))
      l.brightness(targetBrightness, i)

    if doInitColor(i):
      r = int(getRedColor(i))
      g = int(getGreenColor(i))
      b = int(getBlueColor(i))

      log('Setting initial color to rgb(%s, %s, %s) for group %s' % (r,g,b,i))

      l.color(r,g,b,group=i)

  while not monitor.abortRequested():
    if monitor.waitForAbort(10):
      break


