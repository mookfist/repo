from .bridge import WifiBridge

from .bridge import get_bridges
from .actions import fade_brightness
from .actions import fade_color
from .actions import set_color
from .actions import set_brightness
from .actions import set_on
from .actions import set_off
from .actions import set_white

def pprint_bytearray(h):
    s = []
    for i in h:
      try:
        if i == None:
            s.append('None')
        else:
          s.append(hex(i).replace('0x',''))
      except TypeError:
        s.append('%s' % i)

    return ' '.join(s)

