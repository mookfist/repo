class Group():

  def __init__(self, group, **kwargs):
    self.group = group
    self.fadeSteps = kwargs.get('fadeSteps', 1)
    self.brightness = kwargs.get('brightness', 100)
    self.enabled = kwargs.get('enabled', False)
    self.color = kwargs.get('color', 0)
    self.white = kwargs.get('white', False)
    self.color_control = kwargs.get('color_control', False)
