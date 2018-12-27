import utils
import sys, simplejson
import xbmc, xbmcaddon, xbmcgui
from mookfist_lled_controller import scan_bridges
from mookfist_lled_controller.colors import color_from_rgb
from ColorPicker import ColorPicker
import math

__scriptname__ = "Mookfist Milights - Commands"
__author__     =  "Mookfist"
__url__        =  "https://github.com/mookfist/repo"
__settings__   = xbmcaddon.Addon(id='script.service.mookfist-milights')
__version__    = __settings__.getAddonInfo('version')
__kodi_version__ = xbmc.getInfoLabel('System.BuildVersion')

class CustomColorPicker(ColorPicker):
  def __init__(self, *args, **kwargs):
    ColorPicker.__init__(self, *args, **kwargs)
    self.bridge_group = kwargs.get('bridge_group', None)

  def save_color_setting(self, restoreprevious=False):
    if restoreprevious:
      colorname = __settings__.getSetting('group_%s_color_name' % self.bridge_group)
      colorstring = __settings__.getSetting('group_%s_color_value' % self.bridge_group)
    else:
      colorname = self.current_window.getProperty('colorname')
      colorstring = self.current_window.getProperty('colorstring')

    utils.log('save_color_setting: %s %s %s %s' % (
      colorstring,
      type(colorstring),
      colorstring[0:2],
      colorstring[2:2]
    ))

    self.create_color_swatch_image(colorstring)

    r = int(colorstring[0:2], 16)
    g = int(colorstring[2:4], 16)
    b = int(colorstring[4:6], 16)

    color = color_from_rgb(r,g,b)

    __settings__.setSetting('group_%s_color_value' % self.bridge_group, str(color))



def cmd_scan_bridges():

    utils.log('Kodi version: %s' % __kodi_version__)

    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')

#    busy_dialog = xbmcgui.DialogNoCancel()
#    busy_dialog.create()

    utils.log('Scanning for version 4 bridges')
    v4_bridges = scan_bridges(version=4)
    utils.log('Found %s v4 bridges: %s' % (len(v4_bridges), v4_bridges))

    utils.log('Scanning for version 6 bridges')
    v6_bridges = scan_bridges(version=6)
    utils.log('Found %s v6 bridges: %s' % (len(v6_bridges), v6_bridges))

    bridges = []

    for bridge in v4_bridges:
      bridges.append('Version: 4/5 - IP: %s' % bridge[0])

    for bridge in v6_bridges:
      bridges.append('Version: 6 - IP: %s' % bridge[0])


    xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
#    busy_dialog.close()

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

  utils.log('Color picker: %s' % args)

  colorpicker_path = xbmcaddon.Addon("script.module.mooked-colorpicker").getAddonInfo('path').decode('utf-8')
  addon_path = xbmcaddon.Addon('script.service.mookfist-milights').getAddonInfo('path').decode('utf-8')

  color_picker = CustomColorPicker('script-skin_helper_service-ColorPicker.xml', colorpicker_path, 'Default', '1080i',
      skin_color_file = addon_path + '/resources/colors/colors.xml',
      bridge_group = args['group']
  )

  color_picker.doModal()

def cmd_set_to_white(args):
  __settings__.setSetting('group_%s_enable_startup', 'true')
  __settings__.setSetting('group_%s_color_value' % args['group'], 'ffffffff')
  __settings__.setSetting('group_%s_brightness' % args['group'], '100')

def cmd_brightness(args):
  group = args['groups']
  if group == 'all':
    group = (0,)
  elif ',' in group:
    group = group.split(',')
  else:
    group = (group,)

  enabled_groups = [int(grp) for grp in group if __settings__.getSetting('enable_group_%s' % grp) == 'true']

  cmd = {
      'groups': enabled_groups,
      'brightness': int(args['brightness'])
  }

  json = simplejson.dumps(cmd)

  xbmc.executebuiltin('NotifyAll(mookfist-milights, brightness, "' + json + '")')

def cmd_white(args):
  group = args['groups']
  if ',' in group:
    group = group.split(',')
  else:
    group = (group,)

  enabled_groups = [int(grp) for grp in group if __settings__.getSetting('enable_group_%s' % grp) == 'true']

  cmd = {
    'groups': enabled_groups,
    'brightness': 100
  }

  json = simplejson.dumps(cmd)

  xbmc.executebuiltin('NotifyAll(mookfist-milights, white, "' + json + '")')
  xbmc.executebuiltin('NotifyAll(mookfist-milights, brightness, "' + json + '")')

def cmd_color_rgb(args):
  group = args['groups']
  r = args['r']
  g = args['g']
  b = args['b']

  if ',' in group:
    group = group.split(',')
  else:
    group = (group,)

  enabled_groups = [int(grp) for grp in group if __settings__.getSetting('enable_group_%s' % grp) == 'true']

  cmd = {
      'r': int(r),
      'g': int(g),
      'b': int(b),
      'groups': enabled_groups
  }

  json = simplejson.dumps(cmd)
  xbmc.executebuiltin('NotifyAll(mookfist-milights, color-rgb, "' + json + '")')

def cmd_fade_out(args):
  group = args['groups']
  if ',' in group:
    group = [int(grp) for grp in group.split(',')]
  else:
    group = (group,)

  enabled_groups = [int(grp) for grp in group if __settings__.getSetting('enable_group_%s' % grp) == 'true']

  cmd = {
      'groups': enabled_groups
  }

  utils.log('Notify fade-out: %s' % cmd)
  xbmc.executebuiltin('NotifyAll(mookfist-milights, fade-out, "' + simplejson.dumps(cmd) + '")')

def cmd_fade_in(args):

  group = args['groups']
  if ',' in group:
    group = [int(grp) for grp in group.split(',')]
  else:
    group = (group,)

  enabled_groups = [int(grp) for grp in group if __settings__.getSetting('enable_group_%s' % grp) == 'true']

  cmd = {
      'groups': enabled_groups
  }

  if 'speed' in args:
    cmd['speed'] = args['speed']
  else:
    cmd['speed'] = None

  xbmc.executebuiltin('NotifyAll(mookfist-milights, fade-in, "' + simplejson.dumps(cmd) + '")')

def cmd_fade_outin(args):
  if 'groups' not in args:
    group = [0,1,2,3,4]
  elif ',' in args['groups']:
    group = args['groups'].split(',')
  else:
    group = (args['groups'],)

  enabled_groups = [int(grp) for grp in group if __settings__.getSetting('enable_group_%s' % grp) == 'true']

  cmd = {
      'groups': enabled_groups
  }

  if 'speed' in args:
    cmd['speed'] = args['speed']
  else:
    cmd['speed'] = None

  utils.log('Notify fade-outin %s' % cmd)

  xbmc.executebuiltin('NotifyAll(mookfist-milights, fade-outin, "' + simplejson.dumps(cmd) + '")')


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

  utils.log('Script - ARGV: %s' % (argv))
  cmd = argv[0]
  args = parse_args(argv[1:])

  utils.log('Script - Command: %s - Args: %s' % (cmd, args))

  if cmd == 'colorpicker':
    cmd_colorpicker(args)
  elif cmd == 'scan':
    cmd_scan_bridges()
  elif cmd == 'set_to_white':
    cmd_set_to_white(args)
  elif cmd == 'fade_in':
    cmd_fade_in(args)
  elif cmd == 'fade_out':
    cmd_fade_out(args)
  elif cmd == 'fade_outin':
    cmd_fade_outin(args)
  elif cmd == 'white':
    cmd_white(args)
  elif cmd == 'color_rgb':
    cmd_color_rgb(args)
  elif cmd == 'brightness':
    cmd_brightness(args)

if __name__ == "__main__":
    main(sys.argv[1:])

