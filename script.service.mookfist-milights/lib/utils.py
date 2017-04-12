import xbmc
import logging

class KodiLogHandler(logging.Handler):
  def emit(self, record):
    msg = self.format(record)

    if record.levelname == 'DEBUG':
      xbmc.log(msg, xbmc.LOGDEBUG)
    elif record.levelname == 'INFO':
      xbmc.log(msg, xbmc.LOGINFO)
    elif record.levelname == 'WARNING':
      xbmc.log(msg, xbmc.LOGWARNING)
    elif record.levelname == 'ERROR':
      xbmc.log(msg, xbmc.LOGERROR)
    elif record.levelname == 'CRITICAL':
      xbmc.log(msg, xbmc.LOGFATAL)

class KodiLogFormatter(logging.Formatter):
  def format(self, record):
    msg = '[%s] %s' % (record.name, record.msg)
    return msg

def initialize_logger(self):
  logger = logging.getLogger('mlledctrl')
  handler = KodiLogHandler()
  handler.setFormatter(KodiLogFormatter())
  logger.addHandler(handler)
  logger.setLevel(logging.DEBUG)

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


