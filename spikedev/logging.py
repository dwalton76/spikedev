"""
A simple module for logging message with timestamps

.. image:: images/logging.jpg
"""

# spikedev libraries
import utime

def _timestamp():
    """
    Returns:
        str: the current timestamp
    """
    (year, month, day, hour, minute, second, _, _) = utime.localtime()
    ms = utime.ticks_ms() % 1000
    return "%d-%02d-%02d %02d:%02d:%02d.%03d %s" % (
        year,
        month,
        day,
        hour % 12,
        minute,
        second,
        ms,
        "AM" if hour < 12 else "PM",
    )


def log_msg(msg):
    """
    prints a timestamp followed by `msg`

    Args:
        msg (str): the string to print

    Example:

    .. code:: python

        from spikedev.logging import log_msg

        log_msg("Hello World")
    """
    print("%s: %s" % (_timestamp(), msg))
