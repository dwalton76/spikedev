# standard libraries
import utime

# spikedev libraries
from spikedev.logging import log_msg
from spikedev.stopwatch import StopWatch


class Sensor:
    """
    Args:
        desc (str): defaults to None
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
        self.mode = mode
        self.port.device.mode(mode)

    def _ensure_mode(self, mode):
        if self.mode != mode:
            self.set_mode(mode)

    def value(self):
        return self.port.device.get()


class TouchSensorMode:

    # value will be from 0 to 10
    FORCE = 0

    # value will be either 0 or 1
    TOUCH = 1

    # value is one of None, 1, 2 or 3
    TAP = 2

    # value will be from 0 to 10, remembers the highest value
    FPEAK = 3

    # value will be from 380 to 698
    FRAW = 4

    FPRAW = 5

    CALIB = 6


class TouchSensor(Sensor):
    def __init__(self, port, desc=None, mode=TouchSensorMode.TOUCH):
        super().__init__(port, desc)
        self.set_mode(mode)

    def value(self):
        # get() returns a list with a single entry
        return self.port.device.get()[0]

    def is_pressed(self):
        """
        Returns:
            bool: True if the button is currently pressed
        """
        self._ensure_mode(TouchSensorMode.TOUCH)
        return bool(self.value())

    def is_released(self):
        """
        Returns:
            bool: True if the button is currently released
        """
        self._ensure_mode(TouchSensorMode.TOUCH)
        return not bool(self.value())

    def wait_for_pressed(self, timeout_ms=None):
        """
        Args:
            timeout_ms (int): the number of milliseconds to wait

        Returns:
            bool: True if the button was pressed within ``timeout_ms``
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
        Args:
            timeout_ms (int): the number of milliseconds to wait

        Returns:
            bool: True if the button was released within ``timeout_ms``
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
        Args:
            timeout_ms (int): the number of milliseconds to wait

        Returns:
            bool: True if the button was pressed and released within ``timeout_ms``
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
