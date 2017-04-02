import xbmc, xbmcaddon

__scriptname__ = "Mookfist Milights"
__author__     = "Mookfist"
__url__        = "https://github.com/mookfist/repo"
__settings__   = xbmcaddon.Addon(id='script.service.mookfist-milights')
__version__    = __settings__.getAddonInfo('version')
__language__   = __settings__.getLocalizedString

def clamp(n, smallest, largest):
  return max(smallest, min(n, largest))


def loggingEnabled():
  return __settings__.getSetting('enable_logging') == 'true'


def groupEnabled(group):
  return __settings__.getSetting('enable_group%s' % group) == 'true'


def doInitBrightness(group):
  if __settings__.getSetting('global_set_brightness_at_start') == 'true':
    return True


def doInitColor(group):
  if __settings__.getSetting('global_enable_color') == 'true':
    return True


def getIntSetting(setting):
  value = __settings__.getSetting(setting)
  if value == '':
    return None
  else:
    return int(value)


def getClampedIntSetting(setting, smallest, largest):
  value = getIntSetting(setting)
  if value != None:
    value = clamp(value, smallest, largest)
  return value


def getRedColor(group):
  return getClampedIntSetting('global_red_value', 0, 255)


def getGreenColor(group):
  return getClampedIntSetting('global_green_value', 0, 255)


def getBlueColor(group):
  return getClampedIntSetting('global_blue_value', 0, 255)


def getRgbColor(group):
  return (getRedColor(group), getGreenColor(group), getBlueColor(group))


def getMaxBrightness(group):
  return getClampedIntSetting('global_max_brightness', 0, 100)


def getMinBrightness(group):
  return getClampedIntSetting('global_min_brightness', 0, 100)


def getBulbType(group):
  typeNumber = getIntSetting('global_bulb_type')

  if typeNumber == 0:
    return 'white'
  elif typeNumber == 1:
    return 'rgbw'
  else:
    return 'rgb'


def getStepSpeed(group):
  speed = getIntSetting('global_fade_speed')

  if speed == 0:
    step = 1
  elif speed == 1:
    step = 5
  elif speed == 2:
    step = 10
  else:
    step = None

  return step


def getStepSpeed(speed):

  if speed == 0:
    step = 1
  elif speed == 1:
    step = 5
  elif speed == 2:
    step = 10
  else:
    step = None

  return step


def getMainStepSpeed(group):
  speed = getIntSetting('global_fade_speed')
  return getStepSpeed(speed)


def getPauseStepSpeed(group):
  speed = getIntSetting('global_pause_fade_speed')
  log('getPauseStepSpeed(%s) - speed: %s' % (group, speed))

  return getStepSpeed(speed)


def log(msg):
  if loggingEnabled():
    xbmc.log('[mookfist-milights] %s' % msg, xbmc.LOGNOTICE)


def initializeLights():
  host = __settings__.getSetting('light_host')
  port = getIntSetting('light_port')
  bulbType = getBulbType(1)
  wait_duration = float(getIntSetting('command_delay')) / 1000.0

  l = Lights(host, port, bulbType, wait_duration)
  return l

