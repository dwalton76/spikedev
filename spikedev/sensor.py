# standard libraries
import utime

# spikedev libraries
from spikedev.logging import log_msg
from spikedev.stopwatch import StopWatch


class Sensor:
    """
    Args:
        port (hub.port): the hub.port.X for this sensor
        desc (str): description, defaults to None
    """

    def __init__(self, port, desc=None):
        self.port = port
        self.port_letter = str(port)[-2]
        self.desc = desc
        self.mode = None

        # wait for sensor to connect
        while self.port.device is None:
            utime.sleep(0.1)

    def __str__(self):
        if self.desc is not None:
            return self.desc
        else:
            return "{}(port {})".format(self.__class__.__name__, self.port_letter)

    def set_mode(self, mode):
        """
        Set the mode for the sensor to ``mode``
        """
        self.mode = mode
        self.port.device.mode(mode)

    def _ensure_mode(self, mode):
        """
        If the sensor is not in ``mode``, put it in ``mode``.
        """
        if self.mode != mode:
            self.set_mode(mode)

    def value(self):
        """
        Return the current value(s) from the sensor
        """
        return self.port.device.get()


class TouchSensorMode:
    """
    * ``FORCE`` value will be from 0 to 10
    * ``TOUCH`` value will be either 0 or 1
    * ``TAP`` value is one of None, 1, 2 or 3
    * ``FPEAK`` value will be from 0 to 10, remembers the highest value
    * ``FRAW`` value will be from 380 to 698
    * ``FPRAW`` TBD
    * ``CALIB`` TBD
    """
    FORCE = 0
    TOUCH = 1
    TAP = 2
    FPEAK = 3
    FRAW = 4
    FPRAW = 5
    CALIB = 6


class TouchSensor(Sensor):
    """
    .. image:: images/touch-sensor.jpg
    """

    def __init__(self, port, desc=None, mode=TouchSensorMode.TOUCH):
        super().__init__(port, desc)
        self.set_mode(mode)

    def value(self):
        """
        Return the current value of the ``TouchSensor``
        """
        # get() always returns a list with a single entry
        return self.port.device.get()[0]

    def is_pressed(self):
        """
        Set the mode to ``TouchSensorMode.TOUCH``. Return ``True`` if the TouchSensor
        is currently pressed, else return ``False``
        """
        self._ensure_mode(TouchSensorMode.TOUCH)
        return bool(self.value())

    def is_released(self):
        """
        Set the mode to ``TouchSensorMode.TOUCH``. Return ``True`` if the TouchSensor
        is currently released, else return ``False``
        """
        self._ensure_mode(TouchSensorMode.TOUCH)
        return not bool(self.value())

    def wait_for_pressed(self, timeout_ms=None):
        """
        Wait ``timeout_ms`` for the ``TouchSensor`` to be pressed. Return ``True`` if the
        button was pressed within ``timeout_ms``, else return ``False``. If ``timeout_ms``
        is ``None`` this will wait for forever.
        """

        if self.is_pressed():
            log_msg("{} already pressed".format(self))
            return True

        stopwatch = StopWatch()
        stopwatch.start()

        while not self.is_pressed():
            if timeout_ms is not None and stopwatch.value_ms >= timeout_ms:
                log_msg("{} was not pressed within {}ms".format(self, timeout_ms))
                return False

            utime.sleep(0.01)

        log_msg("{} pressed".format(self))
        return True

    def wait_for_released(self, timeout_ms=None):
        """
        Wait ``timeout_ms`` for the ``TouchSensor`` to be released. Return ``True`` if the
        button was released within ``timeout_ms``, else return ``False``. If ``timeout_ms``
        is ``None`` this will wait for forever.
        """

        if self.is_released():
            log_msg("{} already released".format(self))
            return True

        stopwatch = StopWatch()
        stopwatch.start()

        while not self.is_released():
            if timeout_ms is not None and stopwatch.value_ms >= timeout_ms:
                log_msg("{} was not released within {}ms".format(self, timeout_ms))
                return False

            utime.sleep(0.01)

        log_msg("{} released".format(self))
        return True

    def wait_for_bump(self, timeout_ms=None):
        """
        Wait ``timeout_ms`` for the ``TouchSensor`` to be bumped. Return ``True`` if the
        button was bumped within ``timeout_ms``, else return ``False``. If ``timeout_ms``
        is ``None`` this will wait for forever.
        """

        if self.is_pressed():
            if self.wait_for_released(timeout_ms):
                log_msg("{} bumped".format(self))
                return True
            else:
                log_msg("{} was not bumped within {}ms".format(self, timeout_ms))
                return False
        else:
            if self.wait_for_pressed(timeout_ms) and self.wait_for_released(timeout_ms):
                log_msg("{} bumped".format(self))
                return True
            else:
                log_msg("{} was not bumped within {}ms".format(self, timeout_ms))
                return False


def rgb2lab(red, green, blue):
    """
    Convert RGB (``red``, ``green``, ``blue``) to `CIELAB <https://en.wikipedia.org/wiki/CIELAB_color_space>`_
    """

    # XYZ -> Standard-RGB
    # https://www.easyrgb.com/en/math.php
    var_R = red / 255
    var_G = green / 255
    var_B = blue / 255

    if var_R > 0.04045:
        var_R = pow(((var_R + 0.055) / 1.055), 2.4)
    else:
        var_R = var_R / 12.92

    if var_G > 0.04045:
        var_G = pow(((var_G + 0.055) / 1.055), 2.4)
    else:
        var_G = var_G / 12.92

    if var_B > 0.04045:
        var_B = pow(((var_B + 0.055) / 1.055), 2.4)
    else:
        var_B = var_B / 12.92

    var_R = var_R * 100
    var_G = var_G * 100
    var_B = var_B * 100

    X = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805
    Y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722
    Z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505

    reference_X = 95.047
    reference_Y = 100.0
    reference_Z = 108.883

    # XYZ -> CIE-L*ab
    # //www.easyrgb.com/en/math.php
    var_X = X / reference_X
    var_Y = Y / reference_Y
    var_Z = Z / reference_Z

    if var_X > 0.008856:
        var_X = pow(var_X, 1 / 3)
    else:
        var_X = (7.787 * var_X) + (16 / 116)

    if var_Y > 0.008856:
        var_Y = pow(var_Y, 1 / 3)
    else:
        var_Y = (7.787 * var_Y) + (16 / 116)

    if var_Z > 0.008856:
        var_Z = pow(var_Z, 1 / 3)
    else:
        var_Z = (7.787 * var_Z) + (16 / 116)

    L = (116 * var_Y) - 16
    a = 500 * (var_X - var_Y)
    b = 200 * (var_Y - var_Z)

    return (L, a, b)


class ColorSensorMode:
    """
    * ``COLOR`` single value, LED is on
    * ``REFLT`` single value, LED is on,  0 - 100
    * ``AMBI`` single value, LED is off, 0 - 100
    * ``LIGHT`` three values, LED is off, always reads [0, 0, 0], not sure?
    * ``RREFL`` two values, LED is on, not sure?
    * ``RGB_I`` four values, LED is on, (red, green, blue, intensity?)
    * ``HSV`` three values,  LED is on, (hue, saturation, value)
    * ``SHSV``  four values, LED is off, not sure?
    * ``DEBUG`` TBD
    * ``CALIB`` TBD
    """
    COLOR = 0  # single value, LED is on
    REFLT = 1  # single value, LED is on,  0 - 100
    AMBI = 2  # single value, LED is off, 0 - 100
    LIGHT = 3  # three values, LED is off, always reads [0, 0, 0], not sure?
    RREFL = 4  # two values, LED is on, not sure?
    RGB_I = 5  # four values, LED is on, (red, green, blue, intensity?)
    HSV = 6  # three values,  LED is on, (hue, saturation, value)
    SHSV = 7  # four values, LED is off, not sure?
    DEBUG = 8
    CALIB = 9


class ColorSensor(Sensor):
    """
    .. image:: images/color-sensor.jpg
    """

    def __init__(self, port, desc=None, mode=ColorSensorMode.COLOR):
        super().__init__(port, desc)
        self.set_mode(mode)

    def color(self):
        """
        The number of the color. The LED is on.
        """
        self._ensure_mode(ColorSensorMode.COLOR)
        return self.value()[0]

    def reflected_light_intensity(self):
        """
        Set the mode to ``ColorSensorMode.REFLT`` and return the reflected light intensity as a
        percentage (0 to 100). The LED is on.
        """
        self._ensure_mode(ColorSensorMode.REFLT)
        return self.value()[0]

    def ambient_light_intensity(self):
        """
        Set the mode to ``ColorSensorMode.AMBI`` and return the ambient light intensity as a
        percentage (0 to 100). The LED is off.
        """
        self._ensure_mode(ColorSensorMode.AMBI)
        return self.value()[0]

    def hsv(self):
        """
        Set the mode to ``ColorSensorMode.HSR`` and return the Hue, Saturation, Value values.
        The LED is on.
        """
        self._ensure_mode(ColorSensorMode.HSV)
        (hue, saturation, value) = self.value()
        hue = int((hue / 1024) * 255)
        saturation = int((saturation / 1024) * 255)
        value = int((value / 1024) * 255)
        return (hue, saturation, value)

    def rgb(self, scale_by_intensity=True):
        """
        Set the mode to ``ColorSensorMode.RGB_I`` and return the Red, Green, Blue values.
        The LED is on.
        """
        self._ensure_mode(ColorSensorMode.RGB_I)
        (red, green, blue, intensity) = self.value()
        red = int((red / 1024) * 255)
        green = int((green / 1024) * 255)
        blue = int((blue / 1024) * 255)

        if scale_by_intensity:
            intensity_scale = 1024 / intensity
            red = int(red * intensity_scale)
            green = int(green * intensity_scale)
            blue = int(blue * intensity_scale)

        return (red, green, blue)

    def lab(self, scale_by_intensity=True):
        """
        Set the mode to ``ColorSensorMode.RGB_I`` and return the
        `CIELAB <https://en.wikipedia.org/wiki/CIELAB_color_space>`_ values.
        The LED is on.
        """
        (red, green, blue) = self.rgb(scale_by_intensity)
        return rgb2lab(red, green, blue)


class DistanceSensorMode:
    """
    * ``DISTL`` returns a number from 4 to 49
    * ``DISTS`` returns a number from 4 to 24. Does not work from as far away as DISTL
    * ``SINGL`` always returns [18]
    * ``LISTN`` always returns [0]
    * ``TRAW`` returns a number between 80 and 1600
    * ``LIGHT`` always returns [0, 0, 0, 0]
    * ``PING`` always returns [None]
    * ``ADRAW`` always returns [20]
    * ``CALIB`` TBD
    """
    DISTL = 0
    DISTS = 1
    SINGL = 2
    LISTN = 3
    TRAW = 4
    LIGHT = 5
    PING = 6
    ADRAW = 7
    CALIB = 8


class DistanceSensor(Sensor):
    """
    .. image:: images/distance-sensor.jpg
    """

    def __init__(self, port, desc=None, mode=DistanceSensorMode.DISTL):
        super().__init__(port, desc)
        self.set_mode(mode)
