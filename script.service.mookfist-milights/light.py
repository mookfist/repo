import milight
import time

class Lights(object):

  STATE_OFF = 1
  STATE_ON  = 2

  def __init__(self, host, port=8899, bulbtype='rgb'):
    self.host = host
    self.port = 8899
    self.bulbtype = 'rgbw'

    self.group = None

    self.r = 255
    self.g = 80
    self.b = 0
    
    self.light_state = Lights.STATE_OFF

    self.controller = milight.MiLight({'host': self.host})
    self.light = milight.LightBulb(self.bulbtype)

  def initLights(self):
    for i in range(1,3):
      self.controller.send(self.light.on(self.group))
      time.sleep(0.1)

    for i in range(1,3):
      self.controller.send(self.light.brightness(100, self.group))
      time.sleep(0.1)

    for i in range(1,3):
      self.controller.send(self.light.color(milight.color_from_rgb(self.r,self.g,self.b), self.group))
      time.sleep(0.1)

    for i in range(1,3):
      self.controller.send(self.light.brightness(1, self.group))
      time.sleep(0.1)

    for i in range(1,3):
      self.controller.send(self.light.off(self.group))
      time.sleep(0.1)

    self.light_state = Lights.STATE_OFF
    
  def fadeOn(self):
    for i in range(1,100):
      self.controller.send(self.light.brightness(i, self.group))

    self.light_state = Lights.STATE_ON

  def fadeOff(self):
    for i in range(100,1,-1):
      self.controller.send(self.light.brightness(i,self.group))
   
    self.light_state = Lights.STATE_OFF
   
  def isOn(self):
    if self.light_state == Lights.STATE_OFF:
      return False
    return True

  def isOff(self):
    if self.light_state == Lights.STATE_ON:
      return False
    return True

