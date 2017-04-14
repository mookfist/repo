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
from mookfist_lled_controller import color_from_rgb
from mookfist_lled_controller import Command

GROUPS = (1,2,3,4)

def get_bridges(sock=None):

    if sock == None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)

    sock.bind(('', 0))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    counter = 0
    max_tries = 5

    bridges = []

    while counter < max_tries:
        try:
            sock.sendto(bytearray('Link_Wi-Fi'.encode('utf8')), ('255.255.255.255', 48899))
            data = sock.recv(1024)
            if data:
                host, mac = data.split(','.encode('utf8'))[:2]

                bridge = (host.decode('utf8'),mac.decode('utf8'))
                if bridge not in bridges:
                    bridges.append(bridge)
            time.sleep(1)
            counter = counter + 1
        except socket.timeout:
            counter = counter + 1


    return tuple(bridges)

class Bridge(object):
    def __init__(self, ip, port, pause=100, repeat=1, *args, **kwargs):
        self.ip = ip
        self.port = port
        self.pause = pause / 1000.0
        self.repeat = repeat
        self.timeout = kwargs.get('timeout', 2)

        self._groups = {}
        self._Group = kwargs.get('group_class', Group)

        sock = kwargs.get('sock', None)
        if sock == None:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.settimeout(self.timeout)
        else:
            self._sock = sock

        self._last_set_group = -1

        self.logger = logging.getLogger('mlledctrl.bridge4')


    def get_group(self, group):
        if group < 1 or group > 4:
          raise InvalidGroup(group)

        if group not in self._groups:
            self._groups[group] = self._Group(group)
        return self._groups[group]

    def _init_group(self, group=1):
        g = self.get_group(group)
        if self._last_set_group != group:
            self.send(g.on())
            self._last_set_group = group
        return g


    def color(self, color, group=1):
        g = self._init_group(group)
        self.send(g.color(color))

    def color_rgb(self, r, g, b, group=1):
        g = self._init_group(group)
        self.send(g.color_rgb(r,g,b))

    def off(self, group=1):
        g = self.get_group(group)
        self.send(g.off())
        self._last_set_group = -1

    def on(self, group=1):
        g = self.get_group(group)
        self.send(g.on())
        self._last_set_group = group

    def white(self, group=1):
        g = self._init_group(group)
        self.send(g.white())

    def brightness(self, brightness, group=1):
        g = self._init_group(group)
        self.send(g.brightness(brightness))

    def send(self, cmd):
        if type(cmd) == Command:
          cmds = [cmd]
        else:
          cmds = cmd

        for x in range(0, self.repeat):
            for c in cmds:
                if type(c) != Command:
                    self.send(c)
                else:
                    self.logger.debug('Sending command: %s' % c.message_str())
                    self._sock.sendto(c.message(), (self.ip, self.port))
                    time.sleep(self.pause)


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

        cmd = Command(2)

        if self.group == 1:
            cmd[0] = 0x45
        elif self.group == 2:
            cmd[0] = 0x47
        elif self.group == 3:
            cmd[0] = 0x49
        elif self.group == 4:
            cmd[0] = 0x4B
        else:
            raise InvalidGroup()

        cmd[1] = 0x00

        return cmd

    def off(self):
        """
        get the Off command for this group
        """

        cmd = Command(2)
        cmd[1] = 0x00

        if self.group == 1:
            cmd[0] = 0x46
        elif self.group == 2:
            cmd[0] = 0x48
        elif self.group == 3:
            cmd[0] = 0x4A
        elif self.group == 4:
            cmd[0] = 0x4C
        else:
            raise InvalidGroup()

        return cmd

    def color(self, color):
        """get the Color command for this group and color (0-255)"""

        cmd = Command(2)
        cmd[0] = 0x40
        cmd[1] = color

        return cmd

    def color_rgb(self, r, g, b):
        # color is white, so set to white
        if r == 255 and b == 255 and g == 255:
            cmd = (self.white(), self.brightness(100))
        # color is black, so turn off
        elif r == 0 and b == 0 and g == 0:
            cmd = self.off()
        # color is is a shade of grey, so set to white and
        # adjust brightness based on grey scale
        elif r == b and b == g and g == r:
            brightness = int(math.ceil((r / 255.0) * 100.0))
            cmd = (self.white(), self.brightness(brightness))
        else:
            color = color_from_rgb(r, g, b)
            color = color + 171
            if color > 255:
                color = color - 255
            cmd = self.color(color)

        return cmd


    def white(self):

        cmd = Command(2)
        cmd[1] = 0x00
        cmd2 = Command(2)
        cmd2[1] = 0x00

        if self.group == 1:
            cmd[0] = 0x45
            cmd2[0] = 0xc5
        elif self.group == 2:
            cmd[0] = 0x47
            cmd2[0] = 0xc7
        elif self.group == 3:
            cmd[0] = 0x49
            cmd2[0] = 0xc9
        elif self.group == 4:
            cmd[0] = 0x4b
            cmd2[0] = 0xcb

        return (cmd,cmd2)

    def brightness(self, brightness):
        """"get the brightness command for this group and brightness (0-100%)

            LimitlessLED only supports values 2 to 27 for brightness, so this percentage
            is actually a percentage of the value 25

        """
        target_brightness = int(math.ceil(25 * (brightness / 100.0)) + 2)

        """get the Brightness command for this group and brightnes (2-27)"""

        cmd = Command(2)
        cmd[0] = 0x4e
        cmd[1] = target_brightness
        return cmd

