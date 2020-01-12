# Much of the code in this file was ported from ev3dev-lang-python so we
# are including the license for ev3dev-lang-python.

# -----------------------------------------------------------------------------
# Copyright (c) 2015 Ralph Hempel <rhempel@hempeldesigngroup.com>
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


"""
A StopWatch class for tracking the amount of time between events
"""

# standard libraries
import utime


class StopWatch(object):
    """
    A timer class which lets you start a virtual stopwatch and later check
    the amount of time elapsed
    """

    def __init__(self, desc=None):
        """
        Initializes the StopWatch but does not start it.
        """
        self.desc = desc
        self._start_time = None
        self._stopped_total_time = None

    def __str__(self):
        name = self.desc if self.desc is not None else self.__class__.__name__
        return "{}: {}".format(name, self.hms_str)

    def start(self):
        """
        Start the timer. If the timer is already running, raise :py:class:`StopWatchAlreadyStartedException`
        """
        if self.is_started:
            raise StopWatchAlreadyStartedException()

        self._stopped_total_time = None
        self._start_time = utime.ticks_ms()

    def stop(self):
        """
        Stop the timer. The time value of this ``Stopwatch`` is paused and will not continue increasing.
        """
        if self._start_time is None:
            return

        self._stopped_total_time = utime.ticks_ms() - self._start_time
        self._start_time = None

    def reset(self):
        """
        Reset the timer and leave it stopped
        """
        self._start_time = None
        self._stopped_total_time = None

    def restart(self):
        """
        Reset and start the timer
        """
        self.reset()
        self.start()

    @property
    def is_started(self):
        """
        Return ``True`` if the ``StopWatch`` has been started but not stopped
        (i.e., it's currently running), else return ``False``
        """
        return self._start_time is not None

    @property
    def value_ms(self):
        """
        Return the value of the ``StopWatch`` in milliseconds
        """
        if self._stopped_total_time is not None:
            return self._stopped_total_time

        return utime.ticks_ms() - self._start_time if self._start_time is not None else 0

    @property
    def value_secs(self):
        """
        Return the value of the ``StopWatch`` in seconds
        """
        return self.value_ms / 1000

    @property
    def value_hms(self):
        """
        Return the ``StopWatch`` elapsed time as a tuple ``(hours, minutes, seconds, milliseconds)``.
        """
        (hours, x) = divmod(int(self.value_ms), 3600000)
        (mins, x) = divmod(x, 60000)
        (secs, x) = divmod(x, 1000)
        return hours, mins, secs, x

    @property
    def hms_str(self):
        """
        Return the stringified value of the ``StopWatch`` in `HH-MM-SS.msec` format
        """
        return "%02d:%02d:%02d.%03d" % self.value_hms

    def is_elapsed_ms(self, duration_ms):
        """
        Return ``True`` if this timer has measured at least ``duration_ms``
        milliseconds, else returns ``False``. If ``duration_ms`` is None, return ``False``.
        """

        return duration_ms is not None and self.value_ms >= duration_ms

    def is_elapsed_secs(self, duration_secs):
        """
        Return ``True`` if this timer has measured at least ``duration_secs`` seconds,
        else returns ``False``. If ``duration_secs`` is None, returns ``False``.
        """

        return duration_secs is not None and self.value_secs >= duration_secs


class StopWatchAlreadyStartedException(Exception):
    """
    Exception raised when start() is called on a StopWatch which was already start()ed and not yet
    stopped.
    """

    pass
