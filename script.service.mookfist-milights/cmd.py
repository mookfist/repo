import utils
from lib import scanner
import sys
import xbmc, xbmcaddon, xbmcgui

__scriptname__ = "Mookfist Milights - Commands"
__author__     =  "Mookfist"
__url__        =  "https://github.com/mookfist/repo"
__settings__   = xbmcaddon.Addon(id='script.service.mookfist-milights')
__version__    = __settings__.getAddonInfo('version')
__language__   = __settings__.getLocalizedString

if __name__ == "__main__":

    running = True

    dialog = xbmcgui.DialogProgress()
    dialog.create('Scanning')

    while running:
        bridge = scanner.get_bridges()
        if bridge:
            running = False
            __settings__.setSetting('light_host', bridge[0])
    dialog.close()

    utils.log('Hi there from cmd.py - found a bridge: ' + bridge[0])

