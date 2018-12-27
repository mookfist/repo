import xbmc, xbmcaddon
import time, math
import simplejson as json

from lib.utils import Logger
from lib.utils import initialize_logger
from lib.threads.master import MasterThread

from mookfist_lled_controller.colors import color_from_html

__scriptname__ = "Mookfist Milights"
__author__     = "Mookfist"
__url__        = "https://github.com/mookfist/repo"
__settings__   = xbmcaddon.Addon(id='script.service.mookfist-milights')
__version__    = __settings__.getAddonInfo('version')


class ServiceMonitor(xbmc.Monitor):

  def __init__(self, controller_thread):
    xbmc.Monitor.__init__(self)
    self.logger = Logger('mookfist-milights', 'service')
    self.controller_thread = controller_thread
    self.pay_attention = False


  def dispatch_bridge_command(self, method, data):

    self.logger.debug('Dispatching bridge command: %s - %s' % (method, data))

    if method == 'white':
      self.controller_thread.white(data['groups'])
    elif method == 'fade-out':
      self.controller_thread.fade_out(data['groups'])
    elif method == 'fade-in':
      self.controller_thread.fade_in(data['groups'])
    elif method == 'fade-outin':
      self.controller_thread.fade_out(data['groups'], True)
      self.controller_thread.fade_in(data['groups'], True)
    elif method == 'brightness':
      self.controller_thread.brightness(data['brightness'], data['groups'])
    elif method == 'color-rgb':
      self.controller_thread.color_rgb(data['r'], data['b'], data['g'], data['groups'])
    elif method == 'pay-attention':
      self.pay_attention = True

  def dispatch_xbmc_command(self, method, data):
    if method == 'Player.OnPlay':

      if ((self.pay_attention == True)
      or (data['item']['type'] == 'movie' and __settings__.getSetting('autoplay_movie') == 'true')
      or (data['item']['type'] == 'episode' and __settings__.getSetting('autoplay_tv') == 'true')):
        self.controller_thread.reset_queue()
        self.controller_thread.fade_out(self._enabled_groups)
        self.pay_attention = True
    elif method == 'Player.OnStop':
      if ((self.pay_attention == True)
      or (data['item']['type'] == 'movie' and __settings__.getSetting('autoplay_movie') == 'true')
      or (data['item']['type'] == 'episode' and __settings__.getSetting('autplay_tv') == 'true')):
        self.controller_thread.reset_queue()
        self.controller_thread.fade_in(self._enabled_groups)
        self.pay_attention = False


  def onNotification(self, sender, method, data):
    self.logger.debug("SENDER: %s --- METHOD %s --- DATA %s" % (sender, method, data))
    if sender == 'mookfist-milights':
      self.dispatch_bridge_command(method.replace('Other.',''), json.loads(data))
    elif sender == 'xbmc':
      self.dispatch_xbmc_command(method, json.loads(data))


  def onSettingsChanged(self):

    self.logger.debug('Plugin settings have changed')
    self.controller_thread.reload()

if __name__ == "__main__":

  initialize_logger()
  controller = MasterThread(__settings__)
  monitor    = ServiceMonitor(controller)
  controller.start()

  while not monitor.abortRequested():
    if monitor.waitForAbort(100):
      controller.stop()

