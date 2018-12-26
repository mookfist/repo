"""LimitlessLED Version 4 Bridge

This is compatible as well with the version 5 bridge.
"""
import math
import logging
import time
from mookfist_lled_controller.exceptions import InvalidGroup
from mookfist_lled_controller.colors import color_from_rgb
from mookfist_lled_controller.bridge import BaseBridge, BaseGroup, Command

GROUPS = (0, 1, 2, 3, 4, 'all')


class Bridge(BaseBridge):
    """Bridge API

    Valid groups are 1 through 4. You can provide a list of groups
    or use the word 'all' to send the command to all groups.

    >>> bridge = Bridge('192.168.1.100')
    >>> bridge.color(100, [1,2,4])
    >>> bridge.brightness(50, 'all')
    >>> bright.off(3)

    Attributes:
        ip: Bridge IP or hostname
        port: Port number of the bridge
        pause: Number of milliseconds to wait before sending a command
        repeat: Number of times to resend a command
        timeout: Socket timeout
    """
    def __init__(self, ip, port=8899, *args, **kwargs):
        BaseBridge.__init__(self, ip, port, *args, **kwargs)

        self._groups = {}
        self._Group = kwargs.get('group_class', Group)

        self._last_set_group = -1

        self.logger = logging.getLogger('mlledctrl.bridge4')

    def _get_group(self, group):
        if group not in GROUPS:
            raise InvalidGroup(group)

        if group not in self._groups:
            self._groups[group] = self._Group(group)
        return self._groups[group]

    def _init_group(self, group=1):
        g = self._get_group(group)
        if self._last_set_group != group:
            self.on(group)
        return g

    def _send(self, cmd):
        if type(cmd) == Command:
            cmds = [cmd]
        else:
            cmds = cmd

        for x in range(0, self.repeat):
            for c in cmds:
                if type(c) != Command:
                    self._send(c)
                else:
                    self.logger.debug('Sending command: %s' % c.message_str())
                    self._sock.sendto(c.message(), (self.ip, self.port))
                    time.sleep(self.pause)


class Group(BaseGroup):
    """Represents a group of lights

    The Group class is used to get commands specific for a group.

    It has the same interface as the :class:`Bridge` class, but returns instances
    of :class:`Command`.

    Attributes:
        group: Group number bewteen 1 and 4 or 'all'
    """

    def on(self):

        cmd = Command(2)

        if self.group == 1:
            cmd[0] = 0x45
        elif self.group == 2:
            cmd[0] = 0x47
        elif self.group == 3:
            cmd[0] = 0x49
        elif self.group == 4:
            cmd[0] = 0x4B
        elif self.group == 'all' or self.group == 0:
            cmd[0] = 0x42
        else:
            raise InvalidGroup()

        cmd[1] = 0x00

        return cmd

    def off(self):
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
        elif self.group == 'all' or self.group == 0:
            cmd[0] = 0x41
        else:
            raise InvalidGroup()

        return cmd

    def color(self, color):

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
        elif self.group == 'all' or self.group == 0:
            cmd[0] = 0x42
            cmd2[0] = 0xc2

        return (cmd, cmd2)

    def brightness(self, brightness):

        # LimitlessLED only supports values 2 to 27 for brightness, so
        # percentage is actually a percentage of 25.
        target_brightness = int(math.ceil(25 * (brightness / 100.0)) + 2)

        cmd = Command(2)
        cmd[0] = 0x4e
        cmd[1] = target_brightness
        return cmd
