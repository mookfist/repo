import xbmc

class Logger():

  def __init__(self, prefix, name=None):
    self.name = name
    self.prefix = prefix

  def format_msg(self, msg):
    fmsg = '[%s' % self.prefix

    if self.name:
      fmsg = fmsg + '::%s' % self.name

    fmsg = fmsg + '] %s' % msg

    return fmsg

  def debug(self, msg):
    xbmc.log(self.format_msg(msg), xbmc.LOGDEBUG)

  def info(self, msg):
    xbmc.log(self.format_msg(msg), xbmc.LOGINFO)

  def warning(self, msg):
    xbmc.log(self.format_msg(msg), xbmc.LOGWARNING)

  def error(self, msg):
    xbmc.log(self.format_msg(msg), xbmc.LOGERROR)

  def fatal(self, msg):
    xbmc.log(self.format_msg(msg), xbmc.FATAL)


