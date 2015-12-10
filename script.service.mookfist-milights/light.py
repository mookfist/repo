import milight
import time
import threading
from utils import log
from importlib import import_module

SPEED_SLOW = 1
SPEED_MEDIUM = 5
SPEED_FAST = 10

class MilightBulb(milight.LightBulb):

  def __init__(self, types=('rgbw','white','rgb')):
    self.setTypes(types)

  def setTypes(self, types=('rgbw','white','rgb')):
    if type(types) is str:
      types = (types,)

    self._types = []
    for t in types:
      try:
        self._types.append(import_module('.' + t, 'milight'))
      except ImportError:
        print('Unsupported bulb type: %s' % t)

class LightFadeThread(threading.Thread):
  '''Managed fade queues

  Fading works by sending a brightness commands
  This thread manages a queue of brightness adjustment commands
  to get from the current brightness to a target globalMinBrightness
  '''
  def __init__(self, lights):
    threading.Thread.__init__(self)
    self.lights = lights
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
    startingBrightness = self.lights.brightness(group)

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
        self.lights.brightness(task[0], task[1])
      else:
        time.sleep(0.01)


class Light(object):
  '''Represents a Light Group'''
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
    '''turn on lights'''
    self._lightbulb.on(self.group)
    self._on = True

  def brightness(self, brightness=None):
    '''Get and set brightness'''
    if brightness != None:
      self._controller.send(self._lightbulb.brightness(brightness, self.group))
      self._currentBrightness = brightness
    return self._currentBrightness

  def color(self, color=None):
    '''Get and set color'''
    if color != None:
      rgb = milight.color_from_rgb(color[0], color[1], color[2])
      self._controller.send(self._lightbulb.color(rgb, self.group))
      self._currentColor = color
    return self._currentColor


class Lights(object):
  '''API to control multiple light groups'''
  def __init__(self, host, port=8899, bulbtype='rgbw', wait_duration=25):
    '''Constructor

    host - Wifi bridge host or IP address
    port - Wifi bridge port number
    bulbtype - Can be rgbw, rgb, or white
    wait_duration - Interval between sending commands in milliseconds
    '''
    self._host = host
    self._port = port
    self._bulbtype = bulbtype

    self._currentWorkingThread = None

    self._controller = milight.MiLight({'host': self._host, 'port': self._port}, wait_duration=wait_duration / 1000.0)
    self._light = MilightBulb(self._bulbtype)

    self._lights = [None, None, None, None] # four groups maximum


  def setGroupLight(self, group, maxBrightness=100, minBrightness=1, color=(255,255,255)):
    '''Setup lights for a group

    group - Group number for the lights
    maxBrightness - Maximum brightness of the lights (0 to 100)
    minBrightness - Minimum brightness of the lights (100 to 0)
    color - Tuple of red, green, and blue colors, eg (255,255,255) for white
    '''
    self._lights[group-1] = Light((self._controller, self._light), group, maxBrightness, minBrightness, color)

  def removeGroupLight(self, group):
    '''Remove lights for a group'''
    self._lights[group-1] = None

  def setHost(self, host, port=8899):
    '''Set the host and port of the wifi bridge'''
    self._host = host
    self._port = port
    self._controller._hosts = ({'host': host, 'port': port},)

  def setWaitDuration(self, wait_duration):
    '''Set the interval in between commands in milliseconds'''
    self._controller._wait = max(wait_duration / 1000.0, 0)

  def setBulbType(self, bulbtype):
    self._light.setTypes(bulbtype)

  def startFadeThread(self):
    '''Start the worker thread that handles fading'''
    self._currentWorkingThread = LightFadeThread(lights=self)
    self._currentWorkingThread.start()

  def stopFadeThread(self):
    '''Stop the worker thread that handles fading'''
    if self._currentWorkingThread != None:
      self._currentWorkingThread.stop()
      self._currentWorkingThread = None

  def brightness(self, group, brightness=None):
    '''Set a group to a specific brightness level'''
    if len(self._lights) >= group and self._lights[group-1] != None:
      if brightness != None:
        log('Setting brightness for group #%s to %s%%' % (group, brightness))
        return self._lights[group-1].brightness(brightness)
      else:
        return self._lights[group-1].brightness()

  def off(self, group):
    '''Turn off a group'''
    if self._lights[group-1] != None:
      self._lights[group-1].off()

  def on(self, group):
    '''Turn on a group'''
    if self._lights[group-1] != None:
      self._lights[group-1].on()

  def fade(self, group, target, step=1):
    '''Fade a group to a target brightness

    group - group number
    target - target brightness (0 to 100)
    step - Speed (1 is slowest)
    '''

    if len(self._lights) >= group and self._lights[group-1] != None:

      l = self._lights[group-1]

      if l.brightness() != None and l.brightness() > target:
        step = -step

      log('Fading lights for group #%s to %s%% brightness at a rate of %s' % (group, target, step))
      if self._currentWorkingThread == None:
        self.startFadeThread()
      self._currentWorkingThread.stopDimming(group)
      self._currentWorkingThread.fade(target, step, group)


  def color(self, group, rgb=None):
    '''Set color of group

    group - Group number
    rgb - Tuple of red, green, blue values eg: (255,255,255) for white
    '''
    if self._lights[group-1] != None:
      log('Setting colors for group #%s to (%s,%s,%s)' % (group, rgb[0], rgb[1], rgb[2]))
      return self._lights[group-1].color(rgb)

