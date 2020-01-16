# Much of the code in this file was ported from ev3dev-lang-python so we
# are including the license for ev3dev-lang-python.

# -----------------------------------------------------------------------------
# Copyright (c) 2015 Ralph Hempel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------

CENTIMETER_MM = 10
DECIMETER_MM = 100
METER_MM = 1000
INCH_MM = 25.4
FOOT_MM = 304.8
YARD_MM = 914.4
STUD_MM = 8


class DistanceValue:
    """
    A base class for ``Distance`` classes. Do not use this directly. Use one of:

    * :class:`DistanceMillimeters`
    * :class:`DistanceCentimeters`
    * :class:`DistanceDecimeters`
    * :class:`DistanceMeters`
    * :class:`DistanceInches`
    * :class:`DistanceFeet`
    * :class:`DistanceYards`
    * :class:`DistanceStuds`.
    """

    # This allows us to sort lists of DistanceValue objects
    def __lt__(self, other):
        return self.mm < other.mm

    def __rmul__(self, other):
        return self.__mul__(other)


class DistanceMillimeters(DistanceValue):
    """
    Distance in millimeters

    Args:
        millimeters (int): the number of millimeters

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MoveDifferential, MotorSpeedDPS
        from spikedev.unit import DistanceMillimeters, DistanceStuds
        from spikedev.wheel import SpikeWheel

        md = MoveDifferential(hub.port.E, hub.port.F, SpikeWheel, DistanceStuds(11))

        # drive forward 600 millimeters
        md.run_for_distance(DistanceMillimeters(600), MotorSpeedDPS(100))
    """

    def __init__(self, millimeters):
        self.millimeters = millimeters

    def __str__(self):
        return str(self.millimeters) + "mm"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return DistanceMillimeters(self.millimeters * other)

    @property
    def mm(self):
        """
        Returns:
            int: our distance in millimeters
        """
        return self.millimeters


class DistanceCentimeters(DistanceValue):
    """
    Distance in centimeters

    Args:
        centimeters (int): the number of centimeters

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MoveDifferential, MotorSpeedDPS
        from spikedev.unit import DistanceCentimeters, DistanceStuds
        from spikedev.wheel import SpikeWheel

        md = MoveDifferential(hub.port.E, hub.port.F, SpikeWheel, DistanceStuds(11))

        # drive forward 60 centimeters
        md.run_for_distance(DistanceCentimeters(60), MotorSpeedDPS(100))
    """

    def __init__(self, centimeters):
        self.centimeters = centimeters

    def __str__(self):
        return str(self.centimeters) + "cm"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return DistanceCentimeters(self.centimeters * other)

    @property
    def mm(self):
        """
        Returns:
            int: our distance in millimeters
        """
        return self.centimeters * CENTIMETER_MM


class DistanceDecimeters(DistanceValue):
    """
    Distance in decimeters

    Args:
        decimeters (int): the number of decimeters

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MoveDifferential, MotorSpeedDPS
        from spikedev.unit import DistanceDecimeters, DistanceStuds
        from spikedev.wheel import SpikeWheel

        md = MoveDifferential(hub.port.E, hub.port.F, SpikeWheel, DistanceStuds(11))

        # drive forward 6 decimeters
        md.run_for_distance(DistanceDecimeters(6), MotorSpeedDPS(100))
    """

    def __init__(self, decimeters):
        self.decimeters = decimeters

    def __str__(self):
        return str(self.decimeters) + "dm"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return DistanceDecimeters(self.decimeters * other)

    @property
    def mm(self):
        """
        Returns:
            int: our distance in millimeters
        """
        return self.decimeters * DECIMETER_MM


class DistanceMeters(DistanceValue):
    """
    Distance in meters

    Args:
        meters (int): the number of meters

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MoveDifferential, MotorSpeedDPS
        from spikedev.unit import DistanceMeters, DistanceStuds
        from spikedev.wheel import SpikeWheel

        md = MoveDifferential(hub.port.E, hub.port.F, SpikeWheel, DistanceStuds(11))

        # drive forward 2 meters
        md.run_for_distance(DistanceMeters(2), MotorSpeedDPS(100))
    """

    def __init__(self, meters):
        self.meters = meters

    def __str__(self):
        return str(self.meters) + "m"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return DistanceMeters(self.meters * other)

    @property
    def mm(self):
        """
        Returns:
            int: our distance in millimeters
        """
        return self.meters * METER_MM


class DistanceInches(DistanceValue):
    """
    Distance in inches

    Args:
        inches (int): the number of inches

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MoveDifferential, MotorSpeedDPS
        from spikedev.unit import DistanceInches, DistanceStuds
        from spikedev.wheel import SpikeWheel

        md = MoveDifferential(hub.port.E, hub.port.F, SpikeWheel, DistanceStuds(11))

        # drive forward 6 inches
        md.run_for_distance(DistanceInches(6), MotorSpeedDPS(100))
    """

    def __init__(self, inches):
        self.inches = inches

    def __str__(self):
        return str(self.inches) + "in"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return DistanceInches(self.inches * other)

    @property
    def mm(self):
        """
        Returns:
            int: our distance in millimeters
        """
        return self.inches * INCH_MM


class DistanceFeet(DistanceValue):
    """
    Distance in feet

    Args:
        feet (int): the number of feet

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MoveDifferential, MotorSpeedDPS
        from spikedev.unit import DistanceFeet, DistanceStuds
        from spikedev.wheel import SpikeWheel

        md = MoveDifferential(hub.port.E, hub.port.F, SpikeWheel, DistanceStuds(11))

        # drive forward 3 feet
        md.run_for_distance(DistanceFeet(3), MotorSpeedDPS(100))
    """

    def __init__(self, feet):
        self.feet = feet

    def __str__(self):
        return str(self.feet) + "ft"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return DistanceFeet(self.feet * other)

    @property
    def mm(self):
        """
        Returns:
            int: our distance in millimeters
        """
        return self.feet * FOOT_MM


class DistanceYards(DistanceValue):
    """
    Distance in yards

    Args:
        yards (int): the number of yards

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MoveDifferential, MotorSpeedDPS
        from spikedev.unit import DistanceYards, DistanceStuds
        from spikedev.wheel import SpikeWheel

        md = MoveDifferential(hub.port.E, hub.port.F, SpikeWheel, DistanceStuds(11))

        # drive forward 2 yards
        md.run_for_distance(DistanceYards(2), MotorSpeedDPS(100))
    """

    def __init__(self, yards):
        self.yards = yards

    def __str__(self):
        return str(self.yards) + "yd"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return DistanceYards(self.yards * other)

    @property
    def mm(self):
        """
        Returns:
            int: our distance in millimeters
        """
        return self.yards * YARD_MM


class DistanceStuds(DistanceValue):
    """
    Distance in studs

    Args:
        studs (int): the number of LEGO studs

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MoveDifferential, MotorSpeedDPS
        from spikedev.unit import DistanceStuds
        from spikedev.wheel import SpikeWheel

        md = MoveDifferential(hub.port.E, hub.port.F, SpikeWheel, DistanceStuds(11))

        # drive forward 2 studs
        md.run_for_distance(DistanceStuds(6), MotorSpeedDPS(100))
    """

    def __init__(self, studs):
        self.studs = studs

    def __str__(self):
        return str(self.studs) + "stud"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return DistanceStuds(self.studs * other)

    @property
    def mm(self):
        """
        Returns:
            int: our distance in millimeters
        """
        return self.studs * STUD_MM


def distance_in_mm(distance):
    """
    Args:
        distance (DistanceValue, int): the distance to convert to millimeters

    Returns:
        int: ``distance`` converted to millimeters

    Example:

    .. code:: python

        from spikedev.unit import DistanceFeet

        two_feet_in_mm = distance_in_mm(DistanceFeet(2))
    """
    if isinstance(distance, DistanceValue):
        return distance.mm

    # If distance is not a DistanceValue object, treat it as an int of mm
    elif isinstance(distance, (float, int)):
        return distance

    else:
        raise TypeError(type(distance))
