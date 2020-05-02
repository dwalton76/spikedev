# standard libraries
import utime

# third party libraries
import hub

# spikedev libraries
from spikedev.logging import log_msg
from spikedev.stopwatch import StopWatch

_buttons = {}


def _callback(desc, held_ms):
    btn = _buttons.get(desc)
    btn._rxed_callback = True
    btn.held_ms = held_ms
    # log_msg("{} _callback_{} held {}ms".format(btn, desc, held_ms))


def _callback_left(held_ms):
    _callback("left", held_ms)


def _callback_right(held_ms):
    _callback("right", held_ms)


def _callback_center(held_ms):
    _callback("center", held_ms)


def _callback_connect(held_ms):
    _callback("connect", held_ms)


class Button:
    """
    A base class for SPIKE buttons. ``button_name`` must be one of ``left``, ``right``, ``center`` or ``connect``.
    ``desc`` is an optional string that will be using when printing a ``Button`` object.
    """

    def __init__(self, button_name, desc=None):
        super().__init__()
        self.desc = desc
        self._rxed_callback = False
        self._button = None

    def __str__(self):
        if self.desc is not None:
            return self.desc
        else:
            return self.__class__.__name__

    def is_pressed(self):
        """
        Return ``True`` if the button is currently pressed, else return ``False``
        """
        return self._button.is_pressed()

    def was_pressed(self):
        """
        Return ``True`` if the button was pressed since the device started
        or the last time this method was called, else return ``False``
        """
        return self._button.was_pressed()

    def presses(self):
        """
        Return an ``int`` of the number of button presses. Also resets this counter to zero.
        """
        return self._button.presses()

    def is_released(self):
        """
        Return ``True`` if the button is currently released, else return ``False``
        """
        return not self._button.is_pressed()

    def _wait(self, timeout_ms=None):
        stopwatch = StopWatch()
        stopwatch.start()

        # This is ugly but SPIKE does not have the _thread module :(
        while not self._rxed_callback:

            if timeout_ms is not None and stopwatch.value_ms >= timeout_ms:
                return False

            utime.sleep(0.01)

        return True

    def wait_for_pressed(self, timeout_ms=None):
        """
        Wait ``timeout_ms`` for the button to be pressed. Return ``True`` if the
        button was pressed within ``timeout_ms``, else return ``False``. If ``timeout_ms``
        is ``None`` this will wait for forever.
        """

        if self.is_pressed():
            log_msg("{} already pressed".format(self))
            return True

        self._rxed_callback = False

        if self._wait(timeout_ms):
            log_msg("{} pressed".format(self))
            return True
        else:
            log_msg("{} was not pressed within {}ms".format(self, timeout_ms))
            return False

    def wait_for_released(self, timeout_ms=None):
        """
        Wait ``timeout_ms`` for the button to be released. Return ``True`` if the
        button was released within ``timeout_ms``, else return ``False``. If ``timeout_ms``
        is ``None`` this will wait for forever.
        """

        if self.is_released():
            log_msg("{} already released".format(self))
            return True

        self._rxed_callback = False

        if self._wait(timeout_ms):
            log_msg("{} released".format(self))
            return True
        else:
            log_msg("{} was not released within {}ms".format(self, timeout_ms))
            return False

    def wait_for_bump(self, timeout_ms=None):
        """
        Wait ``timeout_ms`` for the button to be bumped. Return ``True`` if the
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


class ButtonLeft(Button):
    def __init__(self, desc=None):
        super().__init__("left", desc)
        _buttons["left"] = self
        self._button = hub.button.left
        self._button.callback(_callback_left)


class ButtonRight(Button):
    def __init__(self, desc=None):
        super().__init__("right", desc)
        _buttons["right"] = self
        self._button = hub.button.right
        self._button.callback(_callback_right)


class ButtonCenter(Button):
    def __init__(self, desc=None):
        super().__init__("center", desc)
        _buttons["center"] = self
        self._button = hub.button.center
        self._button.callback(_callback_center)


class ButtonConnect(Button):
    def __init__(self, desc=None):
        super().__init__("connect", desc)
        _buttons["connect"] = self
        self._button = hub.button.connect
        self._button.callback(_callback_connect)
