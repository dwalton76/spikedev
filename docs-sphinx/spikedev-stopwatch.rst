spikedev.stopwatch
==================

Example
-------

.. code:: python

    from spikedev.button import ButtonCenter
    from spikedev.stopwatch import StopWatch

    button = ButtonCenter()

    sw = StopWatch()
    print("Press the center as soon as possible)
    sw.start()
    button.wait_for_bump()
    sw.stop()
    print("center button pressed in {} ms".format(sw.value_ms))


Classes
-------
.. automodule:: spikedev.stopwatch
    :members:
    :undoc-members:
    :show-inheritance: