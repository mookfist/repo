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

'''
class MyPlayer(xbmc.Player):
  def __init__(self, lights):
    xbmc.Player.__init__(self)
    self.lights = lights

  def onPlayBackPaused(self):
    time.sleep(5)
    self.lights.fadeOn()

  def onPlayBackStarted(self):
    if self.isPlayingVideo():
      tag = self.getVideoInfoTag()
      print "------------ TAG INFO ----------------"
      print tag.getFirstAired()
      print tag.getPremiered()
      print "--------------------------------------"
      self.lights.fadeOff()    

  def onPlayBackStopped(self):
    self.lights.fadeOn()
'''    


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
    self.lights.group = int(__settings__.getSetting('light_group'))

    if playerType == None:
      self.log('Could not determine player type: %s' % data, xbmc.LOGWARNING)
      return

    tvEnabled = __settings__.getSetting('tv_enabled')
    movieEnabled = __settings__.getSetting('movie_enabled')

    self.log('TV Enabled: %s -- Movie Enabled: %s -- Player Type: %s' % (tvEnabled, movieEnabled, playerType))

    if playerType == 'tv' and tvEnabled == 'true':
      self.log('TV show has started playing, time to fade out the lights')
      self.lights.fadeOff()
    elif playerType == 'movie' and movieEnabled == 'true':
      self.log('Movie has started playing, time to fade out the lights')
      self.lights.fadeOff()


  def _onStop(self, data):
    playerType = self._getPlayerType(data)
    self.lights.group = int(__settings__.getSetting('light_group'))

    if playerType == None:
      self.log('Coult not determine player type: %s' % data, xbmc.LOGWARNING)
      return

    if playerType == 'tv' and __settings__.getSetting('tv_enabled') == 'true':
      self.log('TV show has stopped playing, time to fade on the lights')
      self.lights.fadeOn()
    elif playerType == 'movie' and __settings__.getSetting('movie_enabled') == 'true':
      self.log('Movie show has stopped playing, time to fade on the lights')
      self.lights.fadeOn()


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

  l = Lights(__settings__.getSetting('light_host'))
  l.group = int(__settings__.getSetting('light_group'))

  monitor = MyMonitor(lights=l)

  xbmc.log('-- LIGHT GROUP: %s' % l.group)

  if __settings__.getSetting('reset_brightness') == 'true':
    brightness = int(float(__settings__.getSetting('start_brightness')))
    xbmc.log('-- INIT BRIGHTNESS WITH %s' % brightness)
    l.setBrightness(brightness)

  if __settings__.getSetting('enable_color_correction') == 'true':
    r = int(float(__settings__.getSetting('red_value')))
    g = int(float(__settings__.getSetting('green_value')))
    b = int(float(__settings__.getSetting('blue_value')))
    
    xbmc.log('-- INIT COLOR WITH (%s, %s, %s)' % (r, g, b))

    l.setColor(r,g,b)

  while not monitor.abortRequested():
    if monitor.waitForAbort(10):
      break

    
