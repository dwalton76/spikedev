.. spikedev documentation master file, created by
   sphinx-quickstart on Wed Jan 15 18:08:30 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

spikedev
========
spikedev is an open source micropython library for
`LEGO SPIKE <https://education.lego.com/en-us/products/lego-education-spike-prime-set/45678#product>`_.
The goal of this library is to build on the functionality provided by LEGO's ``import hub`` library.
spikedev is not firmware, it is simply a colletion of ``.py`` files that you copy to your SPIKE hub
and then import like any other library.

Many features in spikedev were ported from `ev3dev-lang-python <https://github.com/ev3dev/ev3dev-lang-python>`_.


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