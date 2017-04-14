"""Bridge Abstraction Module

This module can be used instead of directly using version
specific modules. It has the same classes and functions as the version specific
modules.

"""
import socket
import time
import logging

def get_bridges(version=4):
    """Get Bridge

    Returns a list of IP and MAC addresses on the network

    Parameters
    ----------
    version : int
        Which bridge version to use, defaults to 4
    """

    if version == 4 or version == 5:
        from mookfist_lled_controller.bridges.ver4 import get_bridges as gb
    elif version == 6:
        from mookfist_lled_controller.bridges.ver6 import get_bridges as gb
    else:
        raise Exception("Unsupported protocol version: %s" % version)

    return gb()


class WifiBridge(object):
    """WifiBridge Abstraction

    This class abstracts version specific Bridge classes. It has the
    same interface as the version specific classes but you must pass
    the version number to the constructor
    """

    VERSIONS = (4,5,6)
    
    def __init__(self, ip, port, version, pause=100, repeat=1, **kwargs):
        """
        Parameters
        ----------
        ip : IP Address of the wifi bridge
        port : Port number of the wifi bridge
        version : Which LimitlessLED wifi version to use
        pause : Delay in milliseconds between commands
        repeat : Number of times to repeat the same command
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

        self._bridge = Bridge(ip, port, pause, repeat, **kwargs)

    def get_group(self, group=1):
        """Return a Group instance
        
        Parameters
        ----------
        group : int
        """
        
        return self._bridge.get_group(group)

    def color(self, color, group=1):
        """Set the color for a group.

        Color ranges from 0 to 255. The specific color of each value
        differs slightly between bridge versions.

        Parameters
        ----------
        color : int
        group : int
        """
        self._bridge.color(color, group)

    def color_from_rgb(self, r, g, b, group=1):
        """Set the color for a group using RGB values

        Color ranges from 0 to 255. If the color is 0 0 0 the lights
        will turn off. If the color if 255 255 255 the lights will be
        set to white. If the RGB are all equal to a value between 255 and 0,
        the lights will turn white, and the brightness will change accordingly.

        Because saturation is not implemented yet, not all possible values of
        RGB are supported. All RGB values should represent colors with a
        100% saturation.

        This method will be more predictable than WifiBridge.color()

        Parameters
        ----------
        r : int
        b : int
        g : int
        group : int
        """
        self._bridge.color_from_rgb(r,g,b,group)

    def brightness(self, brightness, group=1):
        """Set the brightness for a specific group

        Brightness ranges from 0 to 100.

        Parameters
        ----------
        brightness : int
        group : int
        """
        self._bridge.brightness(brightness, group)

    def white(self, group=1):
        """Turn a group white

        Parameters
        ----------
        group : int
        """
        self._bridge.white(group)

    def on(self, group=1):
        """Turn on a group

        Parameters
        ----------
        group : int
        """
        self._bridge.on(group)

    def off(self, group=1):
        """Turn off a group

        Parameters
        ----------
        group : int
        """
        self._bridge.off(group)

    def send(self, cmd, group=1):
        """Send a command to a group

        The command must be a version specific instance
        of a Command class. You can easily do this by using
        WifiBridge.get_group() and using the Group instance
        to get a version specific Command.

        Parameters
        ----------
        cmd : mookfist_lled_controller.Command
        group : int
        """
        self._bridge.send(cmd, group)
