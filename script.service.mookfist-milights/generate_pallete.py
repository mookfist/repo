r = 255
g = 0
b = 0

mult = 32

colors = []

def hex_from_rgb(r,g,b):
  return '%0.2x%0.2x%0.2x' % (r,g,b)


while r <= 255:
  colors.append(hex_from_rgb(r,g,b))

  if r is 255:
    break

  r = r + mult

  if r > 255:
    r = 255


while g <= 255:
  colors.append(hex_from_rgb(r,g,b))

  if g is 255:
    break

  g = g + mult
  if g > 255:
    g = 255


while r >= 0:
  colors.append(hex_from_rgb(r,g,b))

  if r is 0:
    break

  r = r - mult

  if r < 0:
    r = 0


while b <= 255:
  colors.append(hex_from_rgb(r,g,b))

  if b is 255:
    break

  b = b + mult

  if b > 255:
    b = 255


while g >= 0:
  colors.append(hex_from_rgb(r,g,b))

  if g is 0:
    break

  g = g - mult

  if g < 0:
    g = 0


while r <= 255:

  colors.append(hex_from_rgb(r,g,b))

  if r is 255:
    break

  r = r + mult

  if r > 255:
    r = 255


while b >= 0:

  colors.append(hex_from_rgb(r,g,b))

  if b is 0:
    break

  b = b - mult
  if b < 0:
    b = 0


xml_strings = [
  '    <color name="">ff%s</color>' % color for color in colors
]

xml = '''<?xml version="1.0" encoding="utf-8" standalone="yes" ?>
<colors>
  <palette name="milight">
%s
  </palette>
</colors>
''' % '\n'.join(xml_strings)

print xml
