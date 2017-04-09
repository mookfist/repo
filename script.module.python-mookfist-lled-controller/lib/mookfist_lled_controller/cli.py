"""Stuff for the CLI"""
import sys
import logging
from docopt import docopt
from mookfist_lled_controller import logger
from mookfist_lled_controller import WifiBridge
from mookfist_lled_controller import get_bridges
from mookfist_lled_controller import fade_brightness
from mookfist_lled_controller import fade_color
from mookfist_lled_controller import set_color
from mookfist_lled_controller import set_brightness
from mookfist_lled_controller import set_on
from mookfist_lled_controller import set_off
from mookfist_lled_controller import set_white
from mookfist_lled_controller.exceptions import UnsupportedVersion
from mookfist_lled_controller.exceptions import InvalidGroup
from mookfist_lled_controller.exceptions import NoBridgeFound
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
        elif arguments['brightness']:
            self.action = 'brightness'
        elif arguments['on']:
            self.action = ['on']
        elif arguments['off']:
            self.action = 'off'
        elif arguments['white']:
            self.action = 'white'


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

        self.log.info('Fading lights from %s%% to %s%%' % (start, end))
        fade_brightness(self.bridge, self.arguments['--group'], start, end)

    def action_fadec(self):
        start = int(self.arguments['<start>'])
        end   = int(self.arguments['<end>'])

        self.log.info('Fading to color %s from %s' % (end, start))
        fade_color(self.bridge, self.arguments['--group'], start, end)

    def action_color(self):
        color = int(self.arguments['<color>'])

        self.log.info('Setting color to %s' % color)
        set_color(self.bridge, self.arguments['--group'], color)

    def action_white(self):
        self.log.info('Setting color to white')
        set_white(self.bridge, self.arguments['--group'])

    def action_brightness(self):
        brightness = int(self.arguments['<brightness>'])
        self.log.info('Setting brightness to %s%%' % brightness)
        set_brightness(self.bridge, self.arguments['--group'], brightness)

    def action_on(self):
        self.log.info('Turning lights on')
        set_on(self.bridge, self.arguments['--group'])

    def action_off(self):
        self.log.info('Turning lights off')
        set_off(self.bridge, self.arguments['--group'])

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



    def run(self):
        try:
            if (self.arguments['--host']):
                host = self.arguments['--host']
            else:
                self.log.info('Scanning for bridge...')
                bridges = get_bridge(self.bridge_version)
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
            elif self.arguments['--port']:
                port = int(self.arguments['--port'])

            self.log.info('--- Bridge Details')
            self.log.info('Version: %s' % version)
            self.log.info('IP: %s' % host)
            self.log.info('Port: %s' % port)
            self.log.debug('--- Settings')
            self.log.debug('Pause: %sms' % pause)
            self.log.debug('Command Repeat: %s' % rc)

            self.bridge = WifiBridge(host, port, version, pause, rc)
    
            self.route_action()
        except UnsupportedVersion:
            self.log.error('The chosen bridge version is unsupported')
        except InvalidGroup:
            self.log.error('Groups can be numbered 1 through 4 only')
        except NoBridgeFound:
            self.log.error('Sorry, I was not able to find any bridges. So either give me the IP (and port number) of the bridge you wish to use, or figure out why I can not find any bridges')


