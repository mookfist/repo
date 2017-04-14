"""
Command Interface

Represents an interface for version specific Command classes
"""
class Command(object):

    def __init__(self, size):
        self._cmd = []

        for x in range(0, size):
            self._cmd.append(None)
    
    def __getitem__(self, key):
        key = int(key)
        if key > len(self._cmd):
            raise "Invalid byte"
        else:
            return self._cmd[key]

    def __setitem__(self,key,value):
        key = int(key)
        if key > len(self._cmd):
            raise "Invalid byte"
        else:
            self._cmd[key] = value

    def checksum(self):
        return sum(bytearray(self._cmd))

    def message(self):
        return bytearray(self._cmd)
    
    def message_str(self):

        cmd_str = []

        for cmd_byte in self._cmd:
            if cmd_byte == None:
                cmd_str.append('--')
            else:
                s = hex(cmd_byte).replace('0x','')
                if cmd_byte < 16:
                    s = '0%s' % s
                cmd_str.append(s)
        return ' '.join(cmd_str)



