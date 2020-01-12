spikedev.wheel
==============
A module for classes related to wheels and rims

Example
-------

A scenario where a ``Wheel`` class would be used is when the user needs their
robot to drive for a specific distance. That calculation requires the circumference
of the wheel of the robot.

.. code:: python

    from spikedev.wheel import SpikeWheel

    tire = SpikeWheel()

    # calculate the number of rotations needed to travel forward 500mm
    rotations_for_500mm = 500 / tire.circumference_mm

Classes
-------
.. automodule:: spikedev.wheel
    :members:
    :undoc-members:
    :show-inheritance: