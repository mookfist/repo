from light import Lights
import xbmc
import time

if __name__ == "__main__":
  monitor = xbmc.Monitor()

  l = Lights('192.168.1.167')
  l.group = 1
  l.initLights()

  while not monitor.abortRequested():
    if monitor.waitForAbort(10):
      break

    
