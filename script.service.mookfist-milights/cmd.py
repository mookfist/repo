import utils
from light import Lights, LightFadeThread
from lib import scanner
import sys, simplejson
import xbmc, xbmcaddon, xbmcgui

from ColorPicker import ColorPicker

__scriptname__ = "Mookfist Milights - Commands"
__author__     =  "Mookfist"
__url__        =  "https://github.com/mookfist/repo"
__settings__   = xbmcaddon.Addon(id='script.service.mookfist-milights')
__version__    = __settings__.getAddonInfo('version')
__language__   = __settings__.getLocalizedString

class CustomColorPicker(ColorPicker):
  def save_color_setting(self, restoreprevious=False):
    utils.log('CUSOMT COMLORPOPCIKER SAVE!!!!')
    if restoreprevious:
      colorname = __settings__.getSetting('startup_color_name')
      colorstring = __settings__.getSetting('startup_color_value')
    else:
      colorname = self.current_window.getProperty('colorname')
      colorstring = self.current_window.getProperty('colorstring')

    self.create_color_swatch_image(colorstring)

    utils.log('Setting the setting!')

    __settings__.setSetting('startup_color_value', colorstring)
    __settings__.setSetting('startup_color_name', colorname)


def fade_out(argv):
  group = 'all'
  if argv:
    group = argv[0]

  if group != 'all':
    group = int(group)

  if len(argv) >= 2:
    brightness = int(argv[1])
  else:
    brightness = -1

  data = {
    'group': group,
    'brightness': brightness
  }

  utils.log('data: %s' % (simplejson.dumps(data)))

  xbmc.executebuiltin('NotifyAll(mookfist-milights, fade_out, "' + simplejson.dumps(data) + '")')

def fade_in(argv):
  group = 'all'
  if argv:
    group = argv[0]

  if group != 'all':
    group = int(group)

  data = {
    'group': group,
    'brightness': -1
  }
  xbmc.executebuiltin('NotifyAll(mookfist-milights, fade_in, "' + simplejson.dumps(data) + '")')

def scan_bridges():
    running = True
    dialog = xbmcgui.DialogProgress()
    dialog.create('Scanning')

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

