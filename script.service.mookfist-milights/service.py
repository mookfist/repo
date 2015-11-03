from light import Lights
import xbmc, xbmcaddon
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
    self.lights.fadeOff()    

  def onPlayBackStopped(self):
    self.lights.fadeOn()
       
        

if __name__ == "__main__":

  l = Lights(__settings__.getSetting('light_host'))
  l.group = int(__settings__.getSetting('light_group'))

  monitor = xbmc.Monitor()
  player = MyPlayer(lights=l)

  while not monitor.abortRequested():
    if monitor.waitForAbort(10):
      break

    
