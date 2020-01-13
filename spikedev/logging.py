# spikedev libraries
import utime


def timestamp():
    """
    Return a string of the current timestamp
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
    print("%s: %s" % (timestamp(), msg))
