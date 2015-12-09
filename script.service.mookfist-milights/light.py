import milight
import time
import threading

SPEED_SLOW = 1
SPEED_MEDIUM = 5
SPEED_FAST = 10

class LightFadeThread(threading.Thread):

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
    startingBrightness = self.light.getBrightness(group)

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

    '''
    for i in range(startingBrightness, brightness + step, step):
      self._queue.append((group, i))
    '''


  def run(self):

    while self.running == True:
      if len(self._queue) > 0:
        task = self._queue.pop(0)
        print 'Setting brightness for Group #%s to %s%%' % (task[0], task[1])
        self.light.brightness(task[1], task[0])


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

    self._currentWorkingThread = None

    self.controller = milight.MiLight({'host': self.host, 'port': self.port})
    self.light = milight.LightBulb(self.bulbtype)

  def startFadeThread(self):
    self._currentWorkingThread = LightFadeThread(light=self)
    self._currentWorkingThread.start()

  def stopFadeThread(self):
    if self._currentWorkingThread != None:
      self._currentWorkingThread.stop()
      self._currentWorkingThread = None

  def brightness(self, brightness, group=1):
    self.controller.send(self.light.brightness(brightness, group))
    self._groupStates[group-1]['brightness'] = brightness


  def off(self, group=1):
    self.light.off(group)
    self._groupStates[group-1]['on'] = False


  def on(self, group=1):
    self.light.on(group)
    self._groupStates[group-1]['on'] = True

  def getBrightness(self, group=1):
    return self._groupStates[group-1]['brightness']


  def fade(self, target, step=1, group=1):
    if self._currentWorkingThread == None:
      self.startFadeThread()

    self._currentWorkingThread.stopDimming(group)
    self._currentWorkingThread.fade(target, step, group)


  def fadeIn(self, speed=10, group=1):
    self.fade(100, step=speed, group=group)


  def fadeOut(self, speed=10, group=1):
    speed = speed * -1
    self.fade(1, step=speed, group=group)


  def color(self, r, g, b, group=1):
    mr = milight.color_from_rgb(r,g,b)
    self.controller.send(self.light.color(mr, group))

