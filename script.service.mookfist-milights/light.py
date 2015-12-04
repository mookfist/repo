import milight
import time

SPEED_SLOW = 1
SPEED_MEDIUM = 5
SPEED_FAST = 10

class Lights(object):

  def __init__(self, host, port=8899, bulbtype='rgb'):
    self.host = host
    self.port = port
    self.bulbtype = bulbtype

    self._groupStates = [{
        'brightness': 100,
        'on': True,
    },{
        'brightness': 100,
        'on': True
    },{
        'brightness': 100,
        'on': True
    },{
        'brightness': 100,
        'on': True
    }]

    self.controller = milight.MiLight({'host': self.host, 'port': self.port})
    self.light = milight.LightBulb(self.bulbtype)

    self._brightness = None


  def interrupt(self):
    self._interrupt = True


  def brightness(self, brightness, group=1):
    self.controller.send(self.light.brightness(brightness, group))
    self._groupStates[group-1]['brightness'] = brightness


  def off(self, group=1):
    self.light.off(group)
    self._groupStates[group-1]['on'] = False


  def on(self, group=1):
    self.light.on(group)
    self._groupStates[group-1]['on'] = True


  def fade(self, target, step=1, group=1):
      startingBrightness = self._groupStates[group-1]

      for i in range(startingBrightness, target, step):
          self.brightness(i, group)


  def fadeOn(self, speed=10, group=1):
    self.fade(100, group, speed)


  def fadeOff(self, speed=10, group=1):
    self.fade(1, group, speed*-1)


  def color(self, r, g, b, group=1):
    mr = milight.color_from_rgb(r,g,b)
    self.controller.send(self.light.color(mr, group))

