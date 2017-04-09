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

    if version == 4 or version == 5:
        from mookfist_lled_controller.bridges.ver4 import get_bridge as gb
    elif version == 6:
        from mookfist_lled_controller.bridges.ver6 import get_bridge as gb
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

        if version == 4 or version == 5:
            from mookfist_lled_controller.bridges.ver4 import Bridge
        elif version == 6:
            from mookfist_lled_controller.bridges.ver6 import Bridge
        else:
            raise Exception("Unsupported protocol version: %s" % version)

        self._bridge = Bridge(ip, port, pause, repeat)

    def color(self, color, group=1):
        """
        Set the color for a group.

        Color ranges from 0 to 255, where 0 is red.
        """
        self._bridge.color(color, group)

    def brightness(self, brightness, group=1):
        """
        Set the brightness for a specific group

        Brightness ranges from 2 to 27
        """
        self._bridge.brightness(brightness, group)

    def white(self, group=1):
        self._bridge.white(group)

    def on(self, group=1):
        self._bridge.on(group)

    def off(self, group=1):
        self._bridge.off(group)
