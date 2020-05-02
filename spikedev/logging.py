# standard libraries
import utime


def _timestamp():
    """
    utime.time() only gives second granularity but for debug output we really need
    millisecond granularity. Use utime.ticks_ms to generate a timestamp string. It
    will not give you the correct day, hour, etc but if you call this twice in a row
    100ms apart the timestamps returned will be 100ms apart.

    Returns:
        str: a timestamp in ``YY-MM-DD HH:MM:SS.ms`` format
    """
    year = 2020
    month = 1

    ms = utime.ticks_ms()
    (day, ms) = divmod(ms, 86400000)
    (hour, ms) = divmod(ms, 3600000)
    (minute, ms) = divmod(ms, 60000)
    (second, ms) = divmod(ms, 1000)
    day += 1

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
    Prints a timestamp followed by the ``msg`` string
    """
    print("%s: %s" % (_timestamp(), msg))
