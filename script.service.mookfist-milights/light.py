import milight
import time
import threading
from utils import *

SPEED_SLOW = 1
SPEED_MEDIUM = 5
SPEED_FAST = 10

class LightFadeThread(threading.Thread):
  '''Managed fade queues

  Fading works by sending a brightness commands
  This thread manages a queue of brightness adjustment commands
  to get from the current brightness to a target globalMinBrightness
  '''
  def __init__(self, light):
    threading.Thread.__init__(self)
    self.light = light
    self.running = False

    self._queue = []


  def start(self):
    self.running = True
    threading.Thread.start(self)

  def stop(self):
    self.running = False

  def stopDimming(self, group):
    for queuePos, queueCmd in enumerate(self._queue):
      if queueCmd[0] == group:
        self._queue = [ q for q in self._queue if q[0] != group ]


  def fade(self, brightness, step=1, group=1):
    startingBrightness = self.light.brightness(group)

    groupQueue = []
    for i in range(startingBrightness, brightness + step, step):
      groupQueue.append((group, i))


    if len(self._queue) > 0:
      newQueue = []
      for queuePos, queueValue in enumerate(self._queue):
        newQueue.append(queueValue)
        if len(groupQueue) > 0:
          newQueue.append(groupQueue.pop(0))
      self._queue = newQueue
    else:
      self._queue = groupQueue


  def run(self):
    while self.running == True:
      if len(self._queue) > 0:
        task = self._queue.pop(0)
        self.light.brightness(task[0], task[1])


class Light(object):
  '''Represents a Light

  Technically, this represents a group.
  '''
  def __init__(self, milight, group=1, maxBrightness=100, minBrightness=0, color=(255,255,255)):
    self.maxBrightness = maxBrightness
    self.minBrightness = minBrightness
    self._currentColor = color
    self.group = group

    self._controller = milight[0]
    self._lightbulb  = milight[1]
    self._currentBrightness = None
    self._currnetColor = None

    self._on = False

  def on(self):
    self._lightbulb.on(self.group)
    self._on = True

  def brightness(self, brightness=None):
    if brightness != None:
      self._controller.send(self._lightbulb.brightness(brightness, self.group))
      self._currentBrightness = brightness
    return self._currentBrightness

  def color(self, color=None):
    if color != None:
      rgb = milight.color_from_rgb(color[0], color[1], color[2])
      self._controller.send(self._lightbulb.color(rgb, self.group))
      self._currentColor = color
    return self._currentColor


class Lights(object):

  def __init__(self, host, port=8899, bulbtype='rgbw', wait_duration=25):
    self._host = host
    self._port = port
    self._bulbtype = bulbtype

    self._currentWorkingThread = None

    self._controller = milight.MiLight({'host': self._host, 'port': self._port}, wait_duration=wait_duration / 1000.0)
    self._light = milight.LightBulb(self._bulbtype)

    self._lights = [None, None, None, None] # four groups maximum


  def setGroupLight(self, group, maxBrightness=100, minBrightness=1, color=(255,255,255)):
    self._lights[group-1] = Light((self._controller, self._light), group, maxBrightness, minBrightness, color)

  def removeGroupLight(self, group):
    self._lights[group-1] = None

  def setHost(self, host, port=8899):
    self.host = host
    self.port = int(port)
    self.controller._hosts = ({'host': host, 'port': port})

  def setWaitDuration(self, wait_duration):
    self._controller._wait = max(wait_duration / 1000, 0)

  def startFadeThread(self):
    self._currentWorkingThread = LightFadeThread(light=self)
    self._currentWorkingThread.start()

  def stopFadeThread(self):
    if self._currentWorkingThread != None:
      self._currentWorkingThread.stop()
      self._currentWorkingThread = None

  def brightness(self, group, brightness):
    if self._lights[group-1] != None:
      return self._lights[group-1].brightness(brightness)

  def off(self, group):
    if self._lights[group-1] != None:
      self._lights[group-1].off()

  def on(self, group):
    if self._lights[group-1] != None:
      self._lights[group-1].on()

  def fade(self, group, target, step=1):
    if self._lights[group-1] != None:
      if self._currentWorkingThread == None:
        self.startFadeThread()

      self._currentWorkingThread.stopDimming(group)
      self._currentWorkingThread.fade(target, step, group)

  def color(self, group, rgb=None):
    if self._lights[group-1] != None:
      return self._lights[group-1].color(rgb)

