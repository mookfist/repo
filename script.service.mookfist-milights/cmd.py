import utils
from light import Lights, LightFadeThread
from lib import scanner
import sys, simplejson
import xbmc, xbmcaddon, xbmcgui

__scriptname__ = "Mookfist Milights - Commands"
__author__     =  "Mookfist"
__url__        =  "https://github.com/mookfist/repo"
__settings__   = xbmcaddon.Addon(id='script.service.mookfist-milights')
__version__    = __settings__.getAddonInfo('version')
__language__   = __settings__.getLocalizedString



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

def main(argv):

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



if __name__ == "__main__":
    main(sys.argv[1:])

