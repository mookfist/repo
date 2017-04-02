"""Bridge Abstraction Layer

Provides a consistent way of talking to different Limitless LED
protocols
"""
import socket
import time
import logging

def get_bridge(version=4):
    """Get Bridge

    Returns the ip and mac address of the first availale
    wifi bridge.

    Example:
        ip, mac = GetBridge(ver=6)

    """

    if version == 4:
        from .bridges.ver4 import get_bridge as gb
    else:
        raise Exception("Unsupported protocol version: %s" % version)

    return gb()


class WifiBridge(object):
    """Wifi Bridge Class

    Abstraction against different LimitlessLED bridge versions
    """
    def __init__(self, ip, port, version=4, pause=100, repeat=1):
        """
        ip: IP Address of the wifi bridge
        port: Port number of the wifi bridge
        version: Which LimitlessLED wifi version to use
        pause: Delay in milliseconds between commands
        repeat: Number of times to repeat the same command
        """
        self.ip = ip
        self.port = port
        self.pause = pause / 1000.0
        self.repeat = repeat
        self._groups = {}

        if version == 4:
            from .bridges.ver4 import Group
        else:
            raise Exception("Unsupported protocol version: %s" % version)

        self._Group = Group

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._last_set_group = -1


    def get_group(self, group):
        """
        Get an instance of a Group class for the specific group
        """
        if group not in self._groups:
            self._groups[group] = self._Group(group)
        return self._groups[group]

    def color(self, color, group=1):
        """
        Set the color for a group.

        Color ranges from 0 to 255, where 0 is red.
        """
        g = self.get_group(group)

        if self._last_set_group != group:
            self.send(g.on())
            self._last_set_group = group

        self.send(g.color(color))

    def brightness(self, brightness, group=1):
        """
        Set the brightness for a specific group

        Brightness ranges from 2 to 27
        """
        g = self.get_group(group)

        if self._last_set_group != group:
            self.send(g.on())
            self._last_set_group = group

        self.send(g.brightness(brightness))

    def send(self, cmd):
        """Send a command

        cmd is expected to be array of numbers
        """

        for x in range(0,self.repeat): 
            logging.debug('Sending command: %s' % cmd.message())
            self._sock.sendto(bytearray(cmd.message()), (self.ip, self.port))
            time.sleep(self.pause)


