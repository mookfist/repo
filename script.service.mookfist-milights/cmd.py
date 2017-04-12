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
  def save_color_setting(self, restoreprevious=False):
    if restoreprevious:
      colorname = __settings__.getSetting('startup_color_name')
      colorstring = __settings__.getSetting('startup_color_value')
    else:
      colorname = self.current_window.getProperty('colorname')
      colorstring = self.current_window.getProperty('colorstring')

    self.create_color_swatch_image(colorstring)

    brightness = int(colorstring[:2], 16)

    brightness_percent = (brightness / 255.0) * 100.0

    brightness_percent = int(math.ceil(brightness_percent))

    __settings__.setSetting('startup_color_value', colorstring)
    __settings__.setSetting('startup_color_name', colorname)
    __settings__.setSetting('startup_brightness_value', str(brightness_percent))


def fade_out(argv):
  group = argv['group']

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

    utils.log('Showing bridgelist!!!')

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

#    dialog = xbmcgui.Dialog().select('Bridges', [li])
#    utils.log('%s' % dialog)

#    dialog = xbmcgui.WindowXMLDialog('bridgelist.xml', __settings__.getAddonInfo('path'), 'Default','1080i')
#    dialog.doModal()
    return
    counter = 0
    max_tries = 30

    while running:
        bridge = scanner.get_bridges()
        if bridge:
            running = False
            __settings__.setSetting('light_host', bridge[0])
            __settings__.setSetting('light_port', '8899')
        counter += 1
        if counter > max_tries:
            running = False
            xbmc.executebuiltin('Notification(No Bridges Found, No wifi bridges were detected on your network, 5000)')

    dialog.close()

def cmd_colorpicker(args):

  colorpicker_path = xbmcaddon.Addon("script.module.colorpicker").getAddonInfo('path').decode('utf-8')
  addon_path = xbmcaddon.Addon('script.service.mookfist-milights').getAddonInfo('path').decode('utf-8')

  utils.log('Addon Path: %s' % addon_path)

  color_picker = CustomColorPicker('script-skin_helper_service-ColorPicker.xml', colorpicker_path, 'Default', '1080i',
      skin_color_file = addon_path + '/resources/colors/colors.xml',
      enable_pil = False
  )

  color_picker.doModal()

def cmd_set_to_white(args):
  __settings__.setSetting('startup_color_value','ffffffff')
  __settings__.setSetting('startup_brightness_value', '100')

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
  elif cmd == 'set_color_to_white':
    cmd_set_to_white(args)
  elif cmd == 'fade_in':
    fade_in(args)
  elif cmd == 'fade_out':
    fade_out(args)
  elif cmd == 'fade_outin':
    fade_out(args)
    fade_in(args)
  """


    utils.log(xbmc.translatePath(xbmcaddon.Addon('script.service.mookfist-milights').getAddonInfo('profile')).decode('utf-8'))


    if not argv:
        xbmc.executebuiltin('Notification(Invalid Command, The command module received an invalid command. Chances are that doom will come soon, 5000)')
        return

    if argv[0] == 'scan':
        scan_bridges()
    elif argv[0] == 'fade_out':
        fade_out(argv[1:])
    elif argv[0] == 'fade_in':
        fade_in(argv[1:])
    elif argv[0] == 'fade_outin':
        fade_out(argv[1:])
        fade_in(argv[1:])
  """



if __name__ == "__main__":
    main(sys.argv[1:])

