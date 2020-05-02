spikedev.sensor
===============
A module to interact with the ``color``, ``distance``, and ``touch`` sensors


Example
-------

.. code:: python

    from spikedev.sensor import ColorSensor, TouchSensor

    cs = ColorSensor()
    ts = TouchSensor()

    # when the user presses the TouchSensor, read the RGB values from the ColorSensor
    ts.wait_for_bump()
    print("color sensor RGB values are {}".format(cs.rgb()))


Classes
-------
.. automodule:: spikedev.sensor
    :members:
    :undoc-members:
    :show-inheritance: