# third party libraries
import hub


def progress_bar_image(count, target, count_brightness="9", target_brightness="0"):
    """
    Args:
        count (int): the number of pixels in the progress bar completed
        target (int): the number of pixels in the progress bar total
        count_brightness (str): the intensity of completed pixels
        target_brightness (str): the intensity of remaining ``target`` pixels

    Returns:
        hub.Image: an Image object of the progress bar

    Example:

    .. code:: python

        import hub
        from spikedev.display import progress_bar_image

        pb = progress_bar_image(12, 20)
        hub.display.show(pb)
    """

    if count > target:
        raise ValueError("count {} must be <= target {}".format(count, target))

    result = []
    x = 1
    y = 5
    brightness = "9"

    for i in range(25):

        if i and i % 5 == 0:
            result.append(":")

        if i == count:
            brightness = "4"
        elif i == target:
            brightness = "0"

        result.append(brightness)
        x += 1

        if x == 6:
            x = 1
            y -= 1

    return hub.Image("".join(result))


# hub.display.show(busy_circle, delay=50, fade=1, loop=True)
busy_circle = [
    hub.Image("00900:00000:00000:00000:00000"),
    hub.Image("00090:00000:00000:00000:00000"),
    hub.Image("00000:00009:00000:00000:00000"),
    hub.Image("00000:00000:00009:00000:00000"),
    hub.Image("00000:00000:00000:00009:00000"),
    hub.Image("00000:00000:00000:00000:00090"),
    hub.Image("00000:00000:00000:00000:00900"),
    hub.Image("00000:00000:00000:00000:09000"),
    hub.Image("00000:00000:00000:90000:00000"),
    hub.Image("00000:00000:90000:00000:00000"),
    hub.Image("00000:90000:00000:00000:00000"),
    hub.Image("09000:00000:00000:00000:00000"),
]
