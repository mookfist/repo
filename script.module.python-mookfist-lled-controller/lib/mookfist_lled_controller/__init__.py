from .bridge import WifiBridge

from .bridge import get_bridges
from .actions import fade_brightness
from .actions import fade_color
from .actions import set_color
from .actions import set_brightness
from .actions import set_on
from .actions import set_off
from .actions import set_white
from .actions import set_rgb
from .colors import color_from_rgb
from .colors import color_from_hls
from .colors import color_from_html

def pprint_bytearray(h):
    s = []
    for i in h:
        s.append(hex(i).replace('0x',''))
    return ' '.join(s)
    
