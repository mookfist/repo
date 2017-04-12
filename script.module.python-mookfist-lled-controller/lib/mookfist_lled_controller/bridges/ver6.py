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
from mookfist_lled_controller import pprint_bytearray

GROUPS = (1,2,3,4)

def get_bridges(sock=None):
    """Get available bridges"""

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
            sock.sendto(bytearray('HF-A11ASSISTHREAD'.encode('utf8')), ('255.255.255.255', 48899))
            data = sock.recv(1024)
            if data:
                host, mac = data.split(','.encode('utf8'))[:2]
                bridge = (host.decode('utf8'), mac.decode('utf8'))
                if bridge not in bridges:
                    bridges.append(bridge)
            time.sleep(1)
            counter = counter + 1
        except socket.timeout:
            counter = counter + 1

    return tuple(bridges)


def format_hex(i):
    if i < 16:
        i = hex(i).replace('0x','0x0')
    else:
        i = hex(i)
    return i



class Command(object):
    """A LimitlessLED Command"""

    def __init__(self):
        """
        cmd: command to send
        value: value of command, if any (defaults to 0x00)
        suffix: suffix value at the end of the command if any
        """

        self._cmd = []

        for x in range(0,22):
            self._cmd.append(None)

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


    def __getitem__(self, key):
        key = int(key)
        if key >= len(self._cmd):
            raise "Invalid byte"
        else:
            return self._cmd[key]

    def __setitem__(self, key, value):
        key = int(key)
        if key >= len(self._cmd):
            raise "Invalid byte"
        else:
            self._cmd[key] = value

    def checksum(self, group):
        print "yoooo checksum: %s" % self._cmd[10:21]
        va = bytearray(self._cmd[10:21])
        return sum(va) & 0xff

    def message(self):
        """Get an array representation of the message"""
        return self._cmd

    def message_str(self):
        return pprint_bytearray(self._cmd)


class Bridge(object):

    def __init__(self, ip, port=5987, pause=100, repeat=3, *args, **kwargs):
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

        self.logger = logging.getLogger('mlledctrl.bridge6')

        self._wb1 = None
        self._wb2 = None
        self._cmd_counter = 0x01

    def get_session_ids(self):
        self.logger.debug('Getting session IDs')
        b = [
            0x20,
            0x00,
            0x00,
            0x00,
            0x16,
            0x02,
            0x62,
            0x3a,
            0xd5,
            0xed,
            0xa3,
            0x01,
            0xae,
            0x08,
            0x2d,
            0x46,
            0x61,
            0x41,
            0xa7,
            0xf6,
            0xdc,
            0xaf,
            0xf3,
            0xf7,
            0x00,
            0x00,
            0x1e
        ]


        self.send_raw(bytearray(b))

        data = self._sock.recv(1024)


        if data:

            db = bytearray(data)
            self.logger.debug('Response: %s' % pprint_bytearray(db))

            self._wb1 = db[19]
            self._wb2 = db[20]

            self.logger.debug('Session WB1: %s - Session WB2: %s' % (format_hex(self._wb1), format_hex(self._wb2)))

            self.confirm_init()


    def confirm_init(self):
        b = [
            0x80,
            0x00,
            0x00,
            0x00,
            0x11,
            self._wb1,
            self._wb2,
            0x00,
            self._cmd_counter,
            0x00,
            0x33,
            0x00,
            0x00,
            0x00,

            0x00,
            0x00,
            0x00,

            0x00,
            0x00,
            0x00,

            0x00,
            0x00,
            0x33
        ]

        self.logger.debug('Confirming initialization')
        self.send_raw(bytearray(b))

        data = self._sock.recv(1024)
        self.logger.debug('Response: %s' % pprint_bytearray(bytearray(data)))


    def get_group(self, group):
        if group not in self._groups:
            self._groups[group] = self._Group(group)
        return self._groups[group]

    def color(self, color, group=1):
        g = self.get_group(group)
        self.send(g.color(color))

    def brightness(self, brightness, group=1):
        g = self.get_group(group)
        self.send(g.brightness(brightness))

    def white(self, group=1):
        g = self.get_group(group)
        self.send(g.white())

    def on(self, group=1):
        g = self.get_group(group)
        self.send(g.on(),group)

    def off(self, group=1):
        g = self.get_group(group)
        self.send(g.off(),group)

    def send_raw(self, frame):
        self.logger.debug('Sending frame: %s' % pprint_bytearray(frame))
        self._sock.sendto(frame, (self.ip, self.port))
        self._cmd_counter = (self._cmd_counter + 1) % 255
        time.sleep(self.pause)

    def send(self, cmd, group=1):

        if self._wb1 == None or self._wb2 == None:
            self.get_session_ids()

        cmd[5] = self._wb1
        cmd[6] = self._wb2
        cmd[7] = 0x00
        cmd[8] = self._cmd_counter
        cmd[9] = 0x00

        self.logger.debug('Current cmd: %s' % pprint_bytearray(cmd.message()))

        print "YOOOOOOOO: %s" % cmd

        cmd[21] = cmd.checksum(group)

        for x in range(0, self.repeat):
            self.send_raw(bytearray(cmd.message()))

            response = self._sock.recv(1024)
            self.logger.debug('Response: %s' % pprint_bytearray(bytearray(response)))




class Group(object):
    """Represents a group of lights"""

    def __init__(self, group, bulbtype=0x07):
        """
        group: group number (1-4)
        """
        self.group = group
        self.bulbtype = bulbtype

        self._command_counter = 0

    def _prepare_cmd(self):
        cmd = Command()
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
        """
        get the On command for this group
        """

        cmd = self._prepare_cmd()
        cmd[14] = 0x03
        cmd[15] = 0x01
        return cmd

    def off(self):
        """
        get the Off command for this group
        """
        cmd = self._prepare_cmd()
        cmd[14] = 0x03
        cmd[15] = 0x02
        return cmd

    def color(self, color):
        """get the Color command for this group and color (0-255)"""
        cmd = self._prepare_cmd()
        cmd[14] = 0x01
        cmd[15] = color
        cmd[16] = color
        cmd[17] = color
        cmd[18] = color
        color = color + 176
        if color > 255:
            color = color - 255
        return cmd
        # return Command(0x40, color)

    def white(self):
        cmd = self._prepare_cmd()
        cmd[14] = 0x03
        cmd[15] = 0x05
        return cmd

    def brightness(self, brightness):
        """"get the brightness command for this group and brightness (0-100%)

            LimitlessLED only supports values 2 to 27 for brightness, so this percentage
            is actually a percentage of the value 25

        """
        cmd = self._prepare_cmd()
        cmd[14] = 0x02
        cmd[15] = brightness

        return cmd

