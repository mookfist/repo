"""Action Functions

Helper functions that perform different actions on a bridge
"""

def fade_brightness(bridge, groups, start, end):
    """Fade the brightness of the selected groups"""

    if start > end:
        cmds = list(reversed(range(end, start)))
    else:
        cmds = range(start, end)


    for cmd in cmds:
        for grp in groups:
            bridge.brightness(cmd, int(grp))


def fade_color(bridge, groups, start, end):
    """Fade the color of the selected groups"""
    if start > end:
        cmds = list(reversed(range(end, start)))
    else:
        cmds = range(start, end)

    for cmd in cmds:
        for grp in groups:
            bridge.color(cmd, int(grp))


def set_color(bridge, groups, color):
    """Set the color of the selected groups"""
    for grp in groups:

        bridge.color(color, int(grp))


def set_brightness(bridge, groups, brightness):
    """Set the brightness of the selected groups"""
    for grp in groups:
        bridge.brightness(brightness, int(grp))
