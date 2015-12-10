import xbmc, xbmcaddon

__scriptname__ = "Mookfist Milights"
__author__     = "Mookfist"
__url__        = "https://github.com/mookfist/repo"
__settings__   = xbmcaddon.Addon(id='script.service.mookfist-milights')
__version__    = __settings__.getAddonInfo('version')
__language__   = __settings__.getLocalizedString

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

def getRedColor(group):
  return int(__settings__.getSetting('global_red_value'))

def getGreenColor(group):
  return int(__settings__.getSetting('global_green_value'))

def getBlueColor(group):
  return int(__settings__.getSetting('global_blue_value'))

def getRgbColor(group):
  return (getRedColor(group), getGreenColor(group), getBlueColor(group))

def getMaxBrightness(group):
  return int(__settings__.getSetting('global_max_brightness'))

def getMinBrightness(group):
  return int(__settings__.getSetting('global_min_brightness'))

def getBulbType(group):
  typeNumber = int(__settings__.getSetting('global_bulb_type'))

  if typeNumber == 0:
    return 'white'
  elif typeNumber == 1:
    return 'rgbw'
  else:
    return 'rgb'


def getStepSpeed(group):
  speed = int(__settings__.getSetting('global_fade_speed'))


  if speed == 0:
    step = 1
  elif speed == 1:
    step = 5
  elif speed == 2:
    step = 10
  else:
    step = None

  return step


def log(msg):
  if loggingEnabled():
    xbmc.log('[mookfist-milights] %s' % msg)


def initializeLights():
  host = __settings__.getSetting('light_host')
  port = int(__settings__.getSetting('light_port'))
  bulbType = getBulbType(1)
  wait_duration = float(int(__settings__.getSetting('command_delay'))) / 1000.0

  l = Lights(host, port, bulbType, wait_duration)
  return l


