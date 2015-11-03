from light import Lights
import xbmc, xmbcplugin, xbmcaddon
import time

__scriptname__ = "Mookfist Milights"
__author__     = "Mookfist"
__url__        = "https://github.com/mookfist/repo"
__settings__   = xbmcaddon.Addon(id='script.service.mookfist-milights')
__version__    = __settings__.getAddonInfo('version')
__language__   = __settings__.getLocalizedString


class MyPlayer(xbmc.Player):
  def __init__(self, lights):
    xbmc.Player.__init__(self)
    self.lights = lights
  
  def onPlayBackStarted(self):
    l.fadeOff()    
    xbmc.log('*********SOMETHING STARTED PLAYING', level=xbmc.LOGWARNING)

  def onPlayBackStopped(self):
    xbmc.log('*********SOMETHING STOPPED PLAYING', level=xbmc.LOGWARNING)
    l.fadeOn()
       
        

if __name__ == "__main__":

  l = Lights(__settings__.getSetting('light_host'))
  l.group = __settings__.getSetting('light_group')

  monitor = xbmc.Monitor()
  player = MyPlayer(lights=l)

  while not monitor.abortRequested():
    if monitor.waitForAbort(10):
      break

    
