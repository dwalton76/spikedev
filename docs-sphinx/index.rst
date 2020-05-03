.. spikedev documentation master file, created by
   sphinx-quickstart on Wed Jan 15 18:08:30 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========
spikedev
========
spikedev is an open source micropython library for
`LEGO SPIKE <https://education.lego.com/en-us/products/lego-education-spike-prime-set/45678#product>`_.
The goal of this library is to build on the functionality provided by LEGO's ``import hub`` library.
spikedev is not firmware, it is simply a colletion of ``.py`` files that you copy to your SPIKE hub
and then import like any other library.

Many features in spikedev were ported from `ev3dev-lang-python <https://github.com/ev3dev/ev3dev-lang-python>`_.
If you would like to contribute to spikedev, the source is managed at https://github.com/dwalton76/spikedev .

=======
Example
=======
The following example of ``spikedev.tank.MoveDifferential`` can be used for any tank style robot, just substitute
``SpikeLargeWheel`` for the type of wheel you are using and ``DistanceStuds(19)`` with the number of studs seperating
your wheels. This example is for the `Advanced Driving Base <https://education.lego.com/en-us/lessons/prime-competition-ready/assembling-an-advanced-driving-base>`_

.. image:: images/advanced-driving-base.png

Goals
-----

* turn right 90 degrees
* drive forward 12 inches
* drive halfway around a cirle with a radius of 8 inches

Code
-----
.. code:: python

   # Run via
   #  sudo ampy --port <your-dev-here> run ./demo/tank/advanced-driving-base.py
   import hub
   import math
   from spikedev.motor import MotorSpeedPercent, SpikeLargeMotor, SpikeMediumMotor
   from spikedev.sensor import ColorSensor
   from spikedev.tank import MoveDifferential
   from spikedev.unit import DistanceInches, DistanceStuds
   from spikedev.wheel import SpikeLargeWheel

   adb = MoveDifferential(
      left_motor_port=hub.port.A,
      right_motor_port=hub.port.E,
      wheel_class=SpikeLargeWheel,
      wheel_distance=DistanceStuds(19),
      motor_class=SpikeLargeMotor
   )
   adb.rear_motor = SpikeMediumMotor(hub.port.C)
   adb.front_motor = SpikeMediumMotor(hub.port.D)
   adb.left_color_sensor = ColorSensor(hub.port.B)
   adb.right_color_sensor = ColorSensor(hub.port.F

   adb.turn_right(90, MotorSpeedPercent(20))
   adb.run_for_distance(DistanceInches(12), MotorSpeedPercent(50))
   adb.run_arc_right(DistanceInches(8), DistanceInches(8) * math.pi, MotorSpeedPercent(20))

.. youtube:: vqxpZ1TcWzM

.. toctree::
   :maxdepth: 2
   :caption: Install

   install

.. toctree::
   :maxdepth: 2
   :caption: REPL

   repl

.. toctree::
   :maxdepth: 2
   :caption: API

   spikedev-button
   spikedev-logging
   spikedev-motor
   spikedev-sensor
   spikedev-stopwatch
   spikedev-tank
   spikedev-unit
   spikedev-wheel