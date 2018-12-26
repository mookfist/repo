"""LimitlessLED Version 6 Bridge

"""
import types
import math
import logging
import time
from mookfist_lled_controller.colors import color_from_rgb
from mookfist_lled_controller.bridge import BaseBridge, BaseGroup, Command
import six

GROUPS = (0, 1, 2, 3, 4, 'all')

def format_hex(i):
    if i < 16:
        i = hex(i).replace('0x', '0x0')
    else:
        i = hex(i)
    return i


class CustomCommand(Command):
    """A ver6 Command class."""
    def __init__(self, size):
        super(CustomCommand, self).__init__(size)
        self._set_preamble()

    def _set_preamble(self):
        self[0] = 0x80
        self[1] = 0x00
        self[2] = 0x00
        self[3] = 0x00
        self[4] = 0x11
        self[7] = 0x00
        self[8] = 0x02
        self[9] = 0x00

    def checksum(self):
        """Calculate the checksum value of command"""
        return sum(bytearray(self._cmd[10:21])) & 0xff


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
        group_class: Custom group class
    """
    def __init__(self, ip, port=5987, *args, **kwargs):
        BaseBridge.__init__(self, ip, port, *args, **kwargs)
        self._group_cache = {}
        self._Group = kwargs.get('group_class', Group)

        self.logger = logging.getLogger('mlledctrl.bridge6')


        self._wb1 = None
        self._wb2 = None
        self._cmd_counter = 0x01

        self._last_set_group = None

    def _init_group(self, group=1):
        g = self._get_group(group)
        return g

    def _get_session_ids(self):
        self.logger.debug('Getting session IDs')
        cmd = Command(27)
        cmd[0] = 0x20
        cmd[1] = 0x00
        cmd[2] = 0x00
        cmd[3] = 0x00
        cmd[4] = 0x16
        cmd[5] = 0x02
        cmd[6] = 0x62
        cmd[7] = 0x3a
        cmd[8] = 0xd5
        cmd[9] = 0xed
        cmd[10] = 0xa3
        cmd[11] = 0x01
        cmd[12] = 0xae
        cmd[13] = 0x08
        cmd[14] = 0x2d
        cmd[15] = 0x46
        cmd[16] = 0x61
        cmd[17] = 0x41
        cmd[18] = 0xa7
        cmd[19] = 0xf6
        cmd[20] = 0xdc
        cmd[21] = 0xaf
        cmd[22] = 0xf3
        cmd[23] = 0xf7
        cmd[24] = 0x00
        cmd[25] = 0x00
        cmd[26] = 0x1e

        self._send_raw(cmd)

        data = self._sock.recv(1024)

        if data:

            db = bytearray(data)
            self.logger.debug('Response: %s' % db)

            self._wb1 = db[19]
            self._wb2 = db[20]

            self.logger.debug('Session WB1: %s - Session WB2: %s' % (format_hex(self._wb1), format_hex(self._wb2)))

            self._confirm_init()

    def _confirm_init(self):

        cmd = Command(23)
        cmd[0] = 0x80
        cmd[1] = 0x00
        cmd[2] = 0x00
        cmd[3] = 0x00
        cmd[4] = 0x11
        cmd[5] = self._wb1
        cmd[6] = self._wb2
        cmd[7] = 0x00
        cmd[8] = self._cmd_counter
        cmd[9] = 0x00
        cmd[10] = 0x33
        cmd[11] = 0x00
        cmd[12] = 0x00
        cmd[13] = 0x00
        cmd[14] = 0x00
        cmd[15] = 0x00
        cmd[16] = 0x00
        cmd[17] = 0x00
        cmd[18] = 0x00
        cmd[19] = 0x00
        cmd[20] = 0x00
        cmd[21] = 0x00
        cmd[22] = 0x33

        self.logger.debug('Confirming initialization')
        self._send_raw(cmd)

        data = self._sock.recv(1024)
        self.logger.debug('Response: %s' % bytearray(data))

    def _get_group(self, group):
        if group not in self._group_cache:
            self._group_cache[group] = self._Group(group)
        return self._group_cache[group]

    def _send_raw(self, cmd):
        self.logger.debug('Sending command: %s' % cmd.message())
        self._sock.sendto(cmd.message(), (self.ip, self.port))
        self._cmd_counter = (self._cmd_counter + 1) % 255
        time.sleep(self.pause)

    def _send(self, cmd, group=1):

        if type(cmd) == CustomCommand:
            cmds = [cmd,]
        else:
            cmds = cmd

        for cmd in cmds:
            if self._wb1 == None or self._wb2 == None:
                self._get_session_ids()

            for x in range(0, self.repeat):
                cmd[5] = self._wb1
                cmd[6] = self._wb2
                cmd[7] = 0x00
                cmd[8] = self._cmd_counter
                cmd[9] = 0x00
                cmd[21] = cmd.checksum()

                self._send_raw(cmd)


class Group(BaseGroup):
    """Represents a group of lights"""

    def __init__(self, group, bulbtype=0x07):
        if group == 'all':
            self.group = 0
        else:
            self.group = int(group)

        self.bulbtype = bulbtype

        self._command_counter = 0

    def _prepare_cmd(self):
        cmd = CustomCommand(22)
        cmd[10] = 0x31
        cmd[11] = 0x00
        cmd[12] = 0x00
        cmd[13] = self.bulbtype
        cmd[16] = 0x00
        cmd[17] = 0x00
        cmd[18] = 0x00
        cmd[19] = self.group
        cmd[20] = 0x00
        return cmd


    def on(self):
        cmd = self._prepare_cmd()
        cmd[14] = 0x03
        cmd[15] = 0x01
        return cmd

    def off(self):
        cmd = self._prepare_cmd()
        cmd[14] = 0x03
        cmd[15] = 0x02
        return cmd

    def color_rgb(self, r, g, b):
        if r == 255 and b == 255 and g == 255:
            cmd = (self.white(), self.brightness(100))
        elif r == 0 and b == 0 and g == 0:
            cmd = self.off()
        elif r == b and b == g and g == r:
            brightness = int(math.ceil((r / 255.0) * 100.0))
            cmd = (self.white(), self.brightness(brightness))
        else:
            color = color_from_rgb(r, g, b)
            color = color + 25
            if color > 255:
                color = color - 255
            cmd = self.color(color)

        return cmd


    def color(self, color):
        cmd = self._prepare_cmd()
        cmd[14] = 0x01
        cmd[15] = color
        cmd[16] = color
        cmd[17] = color
        cmd[18] = color
        return cmd

    def white(self):
        cmd = self._prepare_cmd()
        cmd[14] = 0x03
        cmd[15] = 0x05
        return cmd

    def brightness(self, brightness):
        cmd = self._prepare_cmd()
        cmd[14] = 0x02
        cmd[15] = brightness

        return cmd
