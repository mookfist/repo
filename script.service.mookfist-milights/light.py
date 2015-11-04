import milight
import time

class Lights(object):

  def __init__(self, host, port=8899, bulbtype='rgb'):
    self.host = host
    self.port = 8899
    self.bulbtype = 'rgbw'

    self.group = None

    self.r = 255
    self.g = 80
    self.b = 0

    self.controller = milight.MiLight({'host': self.host})
    self.light = milight.LightBulb(self.bulbtype)

    self._brightness = None
    self._interrupt = False


  def interrupt(self):
    self._interrupt = True


  def fadeOn(self):
    if self._brightness == None:
      minRange = 1
    else:
      minRange = self._brightness

    for i in range(minRange,100):
      if self._interrupt == False:
        self._brightness = i
        self.controller.send(self.light.brightness(i, self.group))
      else:
        break

    self._interrupt = False


  def fadeOff(self):
    if self._brightness == None:
      minRange = 100
    else:
      minRange = self._brightness

    for i in range(minRange,1,-1):
      if self._interrupt == False:
        self._brightness = i
        self.controller.send(self.light.brightness(i,self.group))
      else:
        break
    self._interrupt = False   

  def setBrightness(self, brightness):
    self.controller.send(self.light.brightness(brightness, self.group))
    self._brightness = brightness

  def setColor(self, r, g, b):
    self.controller.send(self.light.color(milight.color_from_rgb(r,g,b), self.group))

   
