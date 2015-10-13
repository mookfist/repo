import os, sys
import xbmc, xbmcaddon, xbmcgui, xbmcplugin

from qbittorrent.client import Client

__scriptname__ = "QBittorrent"
__author__     = "Mookfist"
__url__        = "https://gibhub.com/mookfist/repo"
__settings__   = xbmcaddon.Addon(id='plugin.program.qbittorrent')
__cwd__        = __settings__.getAddonInfo('path')
__version__    = __settings__.getAddonInfo('version')
__language__   = __settings__.getLocalizedString

HANDLE = int(sys.argv[1])

class QBittorrentList(xbmcgui.WindowXMLDialog):
  def __init__(self, *args, **kwargs):
    xbmc.log('initting dialog')
    xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
    xbmc.log('yup!')
  
  def onAction(self, act):
    xbmc.log('Action ID: %s' % str(act.getId()))

    xbmc.log(str(act.getButtonCode()))
  
  def onClick(self, controlId):

    if controlId == 866:
      self.close()

    xbmc.log('onClick ' + str(controlId))

xbmc.log('imported the client properly!')

username = __settings__.getSetting('username')
password = __settings__.getSetting('password')
url = __settings__.getSetting('url')

qb = Client(url=url)
qb.login(username, password)

xbmc.log('displaying my dialog?')

for arg in sys.argv:
  xbmc.log('arg: %s' % arg)


# xbmcplugin.setContent(addon_handle, 'programs')

def listTorrents():
  torrents = qb.torrents()

  mode = 1

  for torrent in torrents:

    name = torrent['name']
    name += " [COLOR FFFF0000]" + __language__(30010) + "[/COLOR]" + str(torrent['progress'])
    
    li = xbmcgui.ListItem(name)
    ok = xbmcplugin.addDirectoryItem(handle=HANDLE, url='foobar',listitem=li,isFolder=False)  
    xbmcplugin.endOfDirectory(handle=HANDLE)

listTorrents()

xbmc.log('done')
