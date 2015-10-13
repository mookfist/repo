import os, sys, time
from urlparse import urlparse
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

def get_params():
  param=[]
  paramstring=sys.argv[2]
  if len(paramstring)>=2:
    params=sys.argv[2]
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]
  xbmc.log(str(param))
  return param


def filterDownloading(torrents):
  return [torrent for torrent in torrents if torrent['state'] == 'downloading']

def filterCompleted(torrents):
  return [torrent for torrent in torrents if torrent['progress'] == 1]

def filterQueued(torrents):
  return [torrent for torrent in torrents if torrent['state'] == 'queuedUP' or torrent['state'] == 'queuedDL']


def listTorrents(qb, torrentFilter=None):
  torrents = qb.torrents()

  if torrentFilter != None:
    torrents = torrentFilter(torrents)

  xbmc.log(str(torrents))

  mode = 1

  for torrent in torrents:
    xbmc.log('Found torrent: %s' % torrent['name'])

    progress = str(torrent['progress'] * 100) + '%'

    name = torrent['name']
    name += " [COLOR FFFF0000]" + __language__(30004) + "[/COLOR] " + str(progress)
    
    li = xbmcgui.ListItem(name)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='foobar',listitem=li,isFolder=False)  

  xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), cacheToDisc=False)

  xbmc.log('closing connection')

  time.sleep(1)

def listFolders():
  
  folders = ['Downloading','Completed','Queued','All']

  for folder in folders:
    li = xbmcgui.ListItem(folder)

    url = sys.argv[0] + "?mode=%s" % folder

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)

  xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), cacheToDisc=False)
  


username = __settings__.getSetting('username')
password = __settings__.getSetting('password')
url = __settings__.getSetting('url')

qb = Client(url=url)
qb.login(username, password)

for arg in sys.argv:
  xbmc.log('arg: %s' % arg)

params = get_params()

for param in params:
  xbmc.log('param: %s' % param)

mode = 0

try:
  mode = params['mode']
except:
  pass

if mode == 0:
  listFolders()
elif mode == "Downloading":
  listTorrents(qb, filterDownloading)
elif mode == "Completed":
  listTorrents(qb, filterCompleted)
elif mode == "Queued":
  listTorrents(qb, filterQueued)
elif mode == "All":
  listTorrents(qb)

qb.close()
xbmc.log('done')
