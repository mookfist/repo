"""LimitlessLED Version 4 Module

From what I can gather on http://www.limitlessled.com/dev
this should also be compatible with a version 5 wifi bridge.
"""
import socket
import math
import logging
import time
from mookfist_lled_controller.exceptions import NoBridgeFound
from mookfist_lled_controller.exceptions import InvalidGroup

def get_bridge():
    """Get first available bridge"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    sock.bind(('', 0))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    counter = 0
    max_tries = 5

    while counter < max_tries:
        try:
            sock.sendto('Link_Wi-Fi', ('255.255.255.255', 48899))
            data = sock.recv(1024)
            if data:
                host, mac = data.split(',')[:2]
                return (host, mac)
        except socket.timeout:
            counter = counter + 1

    raise NoBridgeFound()

class Bridge(object):
    def __init__(self, ip, port, pause=100, repeat=1, *args, **kwargs):
        self.ip = ip
        self.port = port
        self.pause = pause / 1000.0
        self.repeat = repeat
        self._groups = {}

        self._Group = kwargs.get('group_class', Group)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._last_set_group = -1

        self.logger = logging.getLogger('bridge')


    def get_group(self, group):
        self.logger.warn('Group: %s' % group)
        self.logger.warn('Groups: %s' % self._groups)
        if group not in self._groups:
            self._groups[group] = self._Group(group)
        return self._groups[group]

    def color(self, color, group=1):
        g = self.get_group(group)
        if self._last_set_group != group:
            self.send(g.on())
            self._last_set_group = group

        self.send(g.color(color))

    def off(self, group=1):
        g = self.get_group(group)
        self.send(g.off())

    def on(self, group=1):
        g = self.get_group(group)
        self.send(g.on())


    def brightness(self, brightness, group=1):
        g = self.get_group(group)

        if self._last_set_group != group:
            self.send(g.on())
            self._last_set_group = group

        self.send(g.brightness(brightness))

    def send(self, cmd):
        for x in range(0, self.repeat):
            self.logger.debug('Sending command: %s' % cmd.message())
            self._sock.sendto(bytearray(cmd.message()), (self.ip, self.port))
            time.sleep(self.pause)



class Command(object):
    """A LimitlessLED Command"""

    def __init__(self, cmd, value=0x00, suffix=None):
        """
        cmd: command to send
        value: value of command, if any (defaults to 0x00)
        suffix: suffix value at the end of the command if any
        """
        self.cmd = cmd
        self.value = value
        self.suffix = suffix

    def message(self):
        """Get an array representation of the message"""
        if self.suffix != None:
            return [self.cmd, self.value, self.suffix]
        else:
            return [self.cmd, self.value]


class Group(object):
    """Represents a group of lights"""

    def __init__(self, group):
        """
        group: group number (1-4)
        """
        self.group = group

    def on(self):
        """
        get the On command for this group
        """
        if self.group == 1:
            cmd = 0x45
        elif self.group == 2:
            cmd = 0x47
        elif self.group == 3:
            cmd = 0x49
        elif self.group == 4:
            cmd = 0x4B
        else:
            raise InvalidGroup() 

        return Command(cmd)

    def off(self):
        """
        get the Off command for this group
        """
        if self.group == 1:
            cmd = 0x46
        elif self.group == 2:
            cmd = 0x48
        elif self.group == 3:
            cmd = 0x4A
        elif self.group == 4:
            cmd = 0x4C
        else:
            raise InvalidGroup()

        return Command(cmd)

    def color(self, color):
        """get the Color command for this group and color (0-255)"""
        color = color + 176
        if color > 255:
            color = color - 255
        return Command(0x40, color)

    def brightness(self, brightness):
        """"get the brightness command for this group and brightness (0-100%)
        
            LimitlessLED only supports values 2 to 27 for brightness, so this percentage
            is actually a percentage of the value 25
        
        """
        target_brightness = int(math.ceil(25 * (brightness / 100.0)) + 2)

        """get the Brightness command for this group and brightnes (2-27)"""
        return Command(0x4E, target_brightness)

