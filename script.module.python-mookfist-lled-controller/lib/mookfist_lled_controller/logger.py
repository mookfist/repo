import logging
from colorama import Fore
import time
import datetime

LVL_NAMES = {
    'DEBUG': Fore.CYAN,
    'INFO': Fore.GREEN,
    'WARNING': Fore.YELLOW,
    'ERROR': Fore.RED,
    'CRTICIAL': Fore.MAGENTA
}

class ColoredFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)
        self.timer = datetime.datetime.now()

    def format(self, record):
        lvlname_color = LVL_NAMES[record.levelname]

        lvlname = record.levelname.ljust(8)

        timestamp = datetime.datetime.now() - self.timer

        lvl = '%s[%s%s%s]' % (Fore.WHITE, lvlname_color, lvlname, Fore.WHITE)
        msg = '%s %s %s%s' % (timestamp, lvl, Fore.RESET, record.msg)
        return msg

def get_logger(name, level=logging.INFO):

    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter())

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
    
