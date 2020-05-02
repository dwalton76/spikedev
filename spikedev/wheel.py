# standard libraries
from math import pi


class Wheel:
    """
    A base class for various types of wheels, tires, etc.  All units are in mm.

    Args:
        diameter_mm (int): the wheel's diameter in millimeters
        width_mm (int): the wheel's width in millimeters

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
    **56mm**

    * part number `39367 <https://brickset.com/parts/design-39367>`_
    * comes in set `45678-1 <https://brickset.com/sets/45678-1/>`_

    .. image:: images/39367.jpeg
    """

    def __init__(self):
        Wheel.__init__(self, 56, 14)


class SpikeLargeWheel(Wheel):
    """
    **88mm**

    * part number `49295 <https://brickset.com/parts/design-49295>`_
    * comes in set `45680-1 <https://brickset.com/sets/45680-1/>`_
    """

    def __init__(self):
        Wheel.__init__(self, 88, 14)
