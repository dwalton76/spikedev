"""
Wheel and Rim classes

A great reference when adding new wheels is http://wheels.sariel.pl/
"""
# standard libraries
from math import pi


class Wheel(object):
    """ 
    A base class for various types of wheels, tires, etc.  All units are in mm.

    One scenario where one of the child classes below would be used is when the
    user needs their robot to drive at a specific speed or drive for a specific
    distance. Both of those calculations require the circumference of the wheel
    of the robot.

    Example:

    .. code:: python

        from spikedev.wheel import SpikeWheel

        tire = SpikeWheel()

        # calculate the number of rotations needed to travel forward 500 mm
        rotations_for_500mm = 500 / tire.circumference_mm
    """

    def __init__(self, diameter_mm, width_mm):
        self.diameter_mm = float(diameter_mm)
        self.width_mm = float(width_mm)
        self.circumference_mm = diameter_mm * pi
        self.radius_mm = float(self.diameter_mm / 2)

    def __str__(self):
        return self.__class__.__name__


class SpikeWheel(Wheel):
    """ 
    part number 39367
    comes in set 45678-1
    """

    def __init__(self):
        Wheel.__init__(self, 56, 14)


class SpikeLargeWheel(Wheel):
    """ 
    part number 49295
    comes in set 45680-1
    """

    def __init__(self):
        Wheel.__init__(self, 88, 14)
