from colorsys import rgb_to_hls
from math import floor
import struct
"""
Color functions

Thanks to McSwindler's python-milights project for this code
"""

def color_from_hls(hue, light, sat, offset=0.0):
    if light > 0.95:
        return 256
    elif light < 0.05:
        return -1
    else:
        hue = (-hue + 1 + offset) % 1
        return int(floor(hue*256))

def color_from_rgb(red, green, blue, offset=0.0):
    r = min(red, 255)
    g = min(green, 255)
    b = min(blue, 255)

    if r > 1 or g > 1 or b > 1:
        r = r / 255.0
        g = g / 255.0
        b = b / 255.0

    h,l,s = rgb_to_hls(r,g,b)

    return color_from_hls(h,l,s,offset)

def color_from_html(hexvalue):
    if '#' in hexvalue:
        hexvalue = hexvalue[1:]

    try:
        unhexed = bytes.fromhex(hexvalue)
    except:

        import binascii
        unhexed = binascii.unhexlify(hexvalue)

    return color_from_rgb(*struct.unpack('BBB', unhexed))
