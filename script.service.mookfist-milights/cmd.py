import utils
from light import Lights, LightFadeThread
from lib import scanner
import sys, simplejson
import xbmc, xbmcaddon, xbmcgui
from mookfist_lled_controller import get_bridges
from ColorPicker import ColorPicker
import math

__scriptname__ = "Mookfist Milights - Commands"
__author__     =  "Mookfist"
__url__        =  "https://github.com/mookfist/repo"
__settings__   = xbmcaddon.Addon(id='script.service.mookfist-milights')
__version__    = __settings__.getAddonInfo('version')

class CustomColorPicker(ColorPicker):
  def __init__(self, *args, **kwargs):
    ColorPicker.__init__(self, *args, **kwargs)
    self.bridge_group = kwargs.get('bridge_group', None)

  def save_color_setting(self, restoreprevious=False):
    if restoreprevious:
      colorname = __settings__.getSetting('group%s_color_name' % self.bridge_group)
      colorstring = __settings__.getSetting('group%s_color_value' % self.bridge_group)
    else:
      colorname = self.current_window.getProperty('colorname')
      colorstring = self.current_window.getProperty('colorstring')

    self.create_color_swatch_image(colorstring)

    brightness = int(colorstring[:2], 16)

    brightness_percent = (brightness / 255.0) * 100.0

    brightness_percent = int(math.ceil(brightness_percent))

    __settings__.setSetting('group%s_color_value' % self.bridge_group, colorstring)
    __settings__.setSetting('group%s_brightness_value' % self.bridge_group, str(brightness_percent))
    __settings__.setSetting('group%s_enable_startup' % self.bridge_group, 'true')


def fade_out(argv):
  group = argv['group']
  if group == 'all':
    groups = (1,2,3,4)
  elif ',' in group:
    groups = group.split(',')
  else:
    groups = [group]

  data = {
      'group': groups
  }
  xbmc.executebuiltin('NotifyAll(mookfist-milights, fadeout, "%s")' % simplejson.dumps(data))
  return
  groups = []

  if group == 'all':
    for x in range(1,5):
      if __settings__.getSetting('enable_group%s' % x) == 'true':
        groups.append(x)
  else:
    groups.append(int(group))

  if len(argv) >= 2:
    brightness = int(argv[1])
  else:
    brightness = -1

  data = {
    'group': group,
    'brightness': brightness
  }

  for x in range(100,-1,-1):
    for group in groups:
      data = {
          'group': group,
          'brightness': x
      }
      xbmc.executebuiltin('NotifyAll(mookfist-milights, brightness, "' + simplejson.dumps(data) + '"')

def fade_in(argv):
  group = argv['group']
  groups = []
  if group == 'all':
    for g in [1,2,3,4]:
      if __settings__.getSetting('enable_group%s' % g) == 'true':
        groups.append(g)
  elif ',' in group:
    groups = group.split(',')
  else:
    groups.append(group)

  data = {
      'group': groups
  }

  xbmc.executebuiltin('NotifyAll(mookfist-milights, fadein, "%s")' % simplejson.dumps(data))
  return
  group = argv['group']

  groups = []

  if group == 'all':
    for x in range(1,5):
      if __settings__.getSetting('enable_group%s' % x) == 'true':
        groups.append(x)
  else:
    groups.append(int(group))

  for x in range(0,101):
    for group in groups:
      data = {
          'group': group,
          'brightness': x
      }
      xbmc.executebuiltin('NotifyAll(mookfist-milights, brightness, "' + simplejson.dumps(data) + '")')

def scan_bridges():

    busy_dialog = xbmcgui.DialogBusy()
    busy_dialog.create()

    v4_bridges = get_bridges(version=4)
    v6_bridges = get_bridges(version=6)

    bridges = []

    for bridge in v4_bridges:
      bridges.append('Version: 4/5 - IP: %s' % bridge[0])

    for bridge in v6_bridges:
      bridges.append('Version: 6 - IP: %s' % bridge[0])


    busy_dialog.close()

    bridge_version, bridge_ip = bridges[xbmcgui.Dialog().select('Bridges', bridges)].split(' - ')

    bridge_version = bridge_version.split(': ')[1]
    bridge_port = 0
    if bridge_version == '4/5':
      bridge_version = 0
      bridge_port = 8899

    elif bridge_version == '6':
      bridge_version = 2
      bridge_port = 5987
    else:
      raise Exception('Invalid Bridge Version?!')

    bridge_ip = bridge_ip.split(': ')[1]

    utils.log('Selected Bridge: %s:%s - Version %s' % (bridge_ip, bridge_port, bridge_version))

    __settings__.setSetting('bridge_version', str(bridge_version))
    __settings__.setSetting('bridge_port', str(bridge_port))
    __settings__.setSetting('bridge_ip', bridge_ip)


def cmd_colorpicker(args):

  colorpicker_path = xbmcaddon.Addon("script.module.colorpicker").getAddonInfo('path').decode('utf-8')
  addon_path = xbmcaddon.Addon('script.service.mookfist-milights').getAddonInfo('path').decode('utf-8')

  utils.log('Addon Path: %s' % addon_path)

  color_picker = CustomColorPicker('script-skin_helper_service-ColorPicker.xml', colorpicker_path, 'Default', '1080i',
      skin_color_file = addon_path + '/resources/colors/colors.xml',
      bridge_group = args['group']
  )

  color_picker.doModal()

def cmd_set_to_white(args):
  __settings__.setSetting('group%s_enable_startup', 'true')
  __settings__.setSetting('group%s_color_value' % args['group'], 'ffffffff')
  __settings__.setSetting('group%s_brightness' % args['group'], '100')

def parse_arg(arg):
  key,value = arg.split('=')
  return (key,value)

def parse_args(args):
  d = {}
  for arg in args:
    key,value = parse_arg(arg)
    d[key] = value

  return d

def main(argv):

  cmd = argv[0]
  args = parse_args(argv[1:])

  utils.log('Script - Command: %s - Args: %s' % (cmd, args))

  if cmd == 'colorpicker':
    cmd_colorpicker(args)
  elif cmd == 'scan':
    scan_bridges()
  elif cmd == 'white':
    cmd_set_to_white(args)
  elif cmd == 'fade_in':
    fade_in(args)
  elif cmd == 'fade_out':
    fade_out(args)
  elif cmd == 'fade_outin':
    fade_out(args)
    fade_in(args)

if __name__ == "__main__":
    main(sys.argv[1:])

