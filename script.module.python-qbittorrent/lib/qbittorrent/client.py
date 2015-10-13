import requests
import logging
import json

try:
  basestring
except NameError:
  basestring = str

class Client(object):
  
  def __init__(self, url):
    """QBittorrent Client

    Arguments:
    url -- URL to QBittorrent web api
    """
    self.url = url
    self._session = None

    self._requests_log = logging.getLogger('requests.packages.urllib3')
    self._requests_log.setLevel(logging.DEBUG)
    self._requests_log.propagate = True

  def _listHashes(self, hashes):
    hashList = [hashes] if instance(hashes, basestring) else hashes
    return "|".join(hashList)

  def _getSession(self):
    if self._session == None:
      self._session = requests.Session()
      self._session.headers.update({'Accept': 'application/json'})
      self._session.headers.update({'X-Request': 'JSON'})
      self._session.headers.update({'X-Requeted-With': 'XMLHttpRequest'})
    return self._session

  def _get(self, url, params=None):
    return self._request(httpverb='get', url=url, params=params)

  def _post(self, url, params=None, data=None):
    return self._request(httpverb='post', url=url, params=params, data=data)

  def _request(self, httpverb, url=None, params=None, data=None):
    s = self._getSession()

    finalUrl = self.url
    if url != None:
      finalUrl = finalUrl + "/" + url

    if httpverb == "get" or httpverb == "GET":
      r = s.get(finalUrl, params=params, auth=self._auth)
    elif httpverb == "post" or httpverb == "POST":
      r = s.post(finalUrl, data=data, auth=self._auth)
    else:
      raise InvalidRequest('Invalid HTTP command: %s' % httpverb)

    r.raise_for_status()

    obj = json.loads(r.text)

    r.close()
    
    return obj

  def close(self):
    s = self._getSession()
    s.close()

  def login(self, username, password):
    """Login

    Arguments:
    username -- username
    password -- password
    """
    self._auth = requests.auth.HTTPDigestAuth(username, password)

  def torrents(self):
    """Get torrent list"""
    return self._get('json/torrents')

  def propertiesGeneral(self, hash):
    """Get torrent generic properties"""
    return self._get('json/propertiesGeneral/%s' % hash)

  def propertiesTrackers(self, hash):
    """Get torrent trackers"""
    return self._get('json/propertiesTrackers/%s' % hash)

  def propertiesFiles(self, hash):
    """Get torrent contents"""
    return self._get('json/propertiesFiles/%s' % hash)

  def transerInfo(self):
    """Get global transfer info"""
    return self._get('json/transferInfo')

  def preferences(self):
    """Get qBittorrent preferences"""
    return self._get('json/preferences')

  def download(self, urls):
    """Download torrent from URL
    
    Pass list of URLs as a list
    """
    urlString = "\n".join(urls)
    payload = {'urls': urlString}

    self._post('command/download', data=payload)

  def addTrackers(self, hash, trackers):
    """Add trackers to torrent
    
    trackers can be a string or a list
    """
    trackersString = "\n".join(trackers)
    payload = {'hash': hash, 'trackers': trackersString}
    
    self._post('command/addTrackers', data=payload)

  def pause(self, hash):
    """Pause torrent"""
    payload = {'hash': hash}
    
    self._post('command/pause', data=payload)

  def pauseAll(self):
    """Pause all torrents"""
    self._post('command/pauseall')

  def resume(self, hash):
    """Resume torrent"""
    payload = {'hash': hash}
    
    self._post('command/resume', data=payload)

  def resumeAll(self):
    """Resume all torrents"""
    self._post('command/resumeall')

  def delete(self, hashes):
    """Delete torrent

    hashes can be a string or a list
    """
    payload = {'hashes': self._listHashes(hashes)}
    self._post('command/delete', data=payload)

  def deletePerm(self, hashes):
    """Delete torrent with download data

    hashes could be a string or a list
    """
    payload = {'hashes': self._listHashes(hashes)}
    self._post('command/deletePerm', data=payload)

  def recheck(self, hashes):
    """Recheck torrent

    hashes could be a string or a list
    """
    payload = {'hashes': self._listHashes(hashes)}
    self._post('command/recheck', data=payload)

  def increasePrio(self, hashes):
    """Increase torrent priority

    hashes could be a string or a list
    """
    payload = {'hashes': self._listHashes(hashes)}
    self._post('command/increasePrio', data=payload)

  def decreasePrio(self, hashes):
    """Decrease torrent priority

    hashes could be a string or a list
    """
    payload = {'hashes': self._listHashes(hashes)}
    self._post('command/decreasePrio', data=payload)

  def topPrio(self, hashes):
    """Maximal torrent priority

    hashes could be a string or a list
    """
    payload = {'hashes': self._listHashes(hashes)}
    self._post('command/topPrio', data=payload)

  def bottomPrio(self, hashes):
    """Minimal torrent priority

    hashes could be a string or a list
    """
    payload = {'hashes': self._listHashes(hashes)}
    self._post('command/bottomPrio', data=payload)

  def setFilePrio(self, hash, id, priority):
    """Set file priority"""
    payload = {'hash': hash, 'id': id, 'priority': priority}
    self._post('command/setFilePrio', data=payload)

  def getGlobalDlLimit(self):
    """Get global download limit"""
    return self._post('command/getGlobalDlLimit').text

  def setGlobalDlLimit(self, limit):
    """Set global download limit"""
    payload = {'limit': limit}
    self._post('command/setGlobalDlLimit', data=payload)

  def getGlobalUpLimit(self):
    """Get global upload limit"""
    return self._post('command/getGlobalUpLimit').text

  def setGlobalUpLimit(self, limit):
    """Set global upload limit"""
    payload = {'limit': limit}
    self._post('command/setGlobalUpLimit', data=payload)

  def getTorrentDlLimit(self, hash):
    """Get torrent download limit"""
    payload = {'hash': hash}
    return self._post('command/getTorrentDlLimit', data=payload).text

  def setTorrentDlLimit(self, hash, limit):
    """Set torrent download limit"""
    payload = {'hash': hash, 'limit': limit}
    self._post('command/setTorrentDlLimit', data=payload)

  def getTorrentUpLimit(self, hash):
    """Get torrent upload limit"""
    payload = {'hash': hash}
    return self._post('command/getTorrentUpLimit', data=payload).text

  def setTorrentUpLimit(self, hash, limit):
    """Set torrent download limit"""
    payload = {'hash': hash, 'limit': limit}
    self._post('command/setTorrentUpLimit', data=payload)

  def setPreferences(self, **kwargs):
    """Set preferences"""
    payload = {'json': json.dumps(kwargs)}
    self._post('command/setPreferences', data=payload)

