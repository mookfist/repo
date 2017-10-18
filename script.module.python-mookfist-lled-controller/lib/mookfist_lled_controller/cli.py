"""CLI Module

This module helps enable the CLI."""
import sys
import logging
import traceback
import time, datetime
from colorama import Fore

from mookfist_lled_controller import scan_bridges
from mookfist_lled_controller import create_bridge

from mookfist_lled_controller import logger
from mookfist_lled_controller.exceptions import UnsupportedVersion
from mookfist_lled_controller.exceptions import InvalidGroup
from mookfist_lled_controller.exceptions import NoBridgeFound

LVL_NAMES = {
    'DEBUG': Fore.CYAN,
    'INFO': Fore.GREEN,
    'WARNING': Fore.YELLOW,
    'ERROR': Fore.RED,
    'CRTICIAL': Fore.MAGENTA
}


class ColoredFormatter(logging.Formatter):
    """Colord log formatter"""
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


def configure_logger(debug=False):
    """Configure a logger with colored output"""

    formatter = logger.ColoredFormatter()
    handler   = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    log = logging.getLogger()

    if debug == True:
        log.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
        handler.setLevel(logging.INFO)

    log.addHandler(handler)

class Main(object):
    """the application"""

    def __init__(self, arguments):

        if arguments['fade']:
            self.action = 'fade'
        elif arguments['fadec']:
            self.action = 'fadec'
        elif arguments['color']:
            self.action = 'color'
        elif arguments['rgb']:
            self.action = 'rgb'
        elif arguments['brightness']:
            self.action = 'brightness'
        elif arguments['on']:
            self.action = ['on']
        elif arguments['off']:
            self.action = 'off'
        elif arguments['white']:
            self.action = 'white'
        elif arguments['colorcycle']:
            self.action = 'colorcycle'


        if arguments['--bridge-version'] == '4' or arguments['--bridge-version'] == '5':
            self.bridge_version = 4
        elif arguments['--bridge-version'] == '6':
            self.bridge_version = 6
        elif arguments['--bridge-version'] != None:
            raise UnsupportedVersion
        else:
            self.bridge_version = 4

        self.log = logging.getLogger('lled')

        self.arguments = arguments

    def action_fade(self):
        start = int(self.arguments['<start>'])
        end   = int(self.arguments['<end>'])

        if (start > end):
            steps = -1
        else:
            steps = 1


        self.log.info('Transitioning brightness from %s%% to %s%%' % (start, end))

        self.bridge.on(self.arguments['--group'])

        for brightness in range(start, end, steps):
            self.bridge.brightness(brightness, self.arguments['--group'])

    def action_fadec(self):
        start = int(self.arguments['<start>'])
        end   = int(self.arguments['<end>'])

        if (start > end):
            steps = -1
        else:
            steps = 1

        self.log.info('Transitioning color from %s to %s' % (start, end))

        for color in range(start,end,steps):
            self.bridge.color(color, self.arguments['--group'])

    def action_color(self):
        color = int(self.arguments['<color>'])
        self.log.info('Setting color to %s' % color)
        self.bridge.color(color, self.arguments['--group'])

    def action_white(self):
        self.log.info('Setting color to white')
        self.bridge.white(self.arguments['--group'])

    def action_brightness(self):
        brightness = int(self.arguments['<brightness>'])
        self.log.info('Setting brightness to %s%%' % brightness)
        self.bridge.brightness(self.arguments['--group'])

    def action_on(self):
        self.log.info('Turning lights on')
        self.bridge.on(self.arguments['--group'])

    def action_off(self):
        self.log.info('Turning lights off')
        self.bridge.off(self.arguments['--group'])

    def action_rgb(self):
        r = int(self.arguments['<r>'])
        g = int(self.arguments['<g>'])
        b = int(self.arguments['<b>'])

        self.log.info('Setting color to rgb(%s, %s, %s)' % (r, g, b))
        self.bridge.color_rgb(r, g, b, self.arguments['--group'])


    def action_colorcycle(self):
        for x in range(0,256):
            if x < 0:
                x = x + 255
            elif x > 255:
                x = x - 255
            self.log.info('Setting color to %s' % x)
            self.bridge.color(x, self.arguments['--group'])


    def route_action(self):
        if self.arguments['fade']:
            self.action_fade()
        elif self.arguments['fadec']:
            self.action_fadec()
        elif self.arguments['color']:
            self.action_color()
        elif self.arguments['brightness']:
            self.action_brightness()
        elif self.arguments['on']:
            self.action_on()
        elif self.arguments['off']:
            self.action_off()
        elif self.arguments['white']:
            self.action_white()
        elif self.arguments['rgb']:
            self.action_rgb()
        elif self.arguments['colorcycle']:
            self.action_colorcycle()


    def run(self):
        try:
            if (self.arguments['--bridge-ip']):
                host = self.arguments['--bridge-ip']
            else:
                self.log.info('Scanning for bridge...')
                bridges = scan_bridges(self.bridge_version)
                self.log.info('Found %s bridge(s)' % len(bridges))

                if len(bridges) > 1:
                    self.log.warning('Multiple bridges have been found. I will choose the first one I saw')
                    self.log.warning('If you really don\'t want me to do that, then use the --bridge-ip (and --bridge-port if needed) flags when using this tool')

                    self.log.info('--- Available Bridges')
                    for bridge in bridges:
                        self.log.info('    %s - %s' % (bridge[0], bridge[1]))
                elif len(bridges) == 0:
                    raise NoBridgeFound

                host = bridges[0][0]


            rc = 1
            if self.arguments['--repeat']:
                rc = int(self.arguments['--repeat'])

            pause = 100
            if self.arguments['--pause']:
                pause = int(self.arguments['--pause'])

            version = 4
            if self.arguments['--bridge-version']:
                version = int(self.arguments['--bridge-version'])

            if version == 4 or version == 5:
                port = 8899
            elif version == 6:
                port = 5987
            elif self.arguments['--bridge-port']:
                port = int(self.arguments['--bridge-port'])

            self.log.info('--- Bridge Details')
            self.log.info('Version: %s' % version)
            self.log.info('IP: %s' % host)
            self.log.info('Port: %s' % port)
            self.log.debug('--- Settings')
            self.log.debug('Pause: %sms' % pause)
            self.log.debug('Command Repeat: %s' % rc)

            self.bridge = create_bridge(version, host, port, pause, rc)

            self.route_action()
        except UnsupportedVersion:
            self.log.error('The chosen bridge version is unsupported')
        except InvalidGroup as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.log.error('Groups can be numbered 1 through 4 only')
            self.log.error(traceback.format_exception(exc_type, exc_value, exc_traceback))
        except NoBridgeFound:
            self.log.error('Sorry, I was not able to find any bridges. So either give me the IP (and port number) of the bridge you wish to use, or figure out why I can not find any bridges')


