from light import Lights
import xbmc
import time

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

  l = Lights('192.168.1.167')
  l.group = 1

  monitor = xbmc.Monitor()
  player = MyPlayer(l)

  while not monitor.abortRequested():
    if monitor.waitForAbort(10):
      break

    
