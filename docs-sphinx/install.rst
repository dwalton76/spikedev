=============
Install Steps
=============

ampy
====
Install `ampy <https://learn.adafruit.com/micropython-basics-load-files-and-run-code/install-ampy>`_ on your
laptop. We will use ampy to communicate with the SPIKE hub via its USB port::

    $ sudo pip3 install adafruit-ampy


Booting SPIKE
=============
The SPIKE UI (heart picture, click left/right to select a program, etc) is produced
by a program on the SPIKE hub called ``main.py`` that runs when the hub boots. We
need to boot the SPIKE hub so that ``main.py`` does not run (long story).

To do this hold down the left button when you press the big circle button to boot SPIKE.
You will not see the heart picture or hear the familiar chime, that is expected. You should
however see the circle button turn white.

Install spikedev
================
We need to create a ``spikedev`` directory on SPIKE and copy all of the spikedev files to that
directory. To do that run::

    $ git clone https://github.com/dwalton76/spikedev.git
    $ cd spikedev
    $ sudo python3 ./utils/spike-install-spikedev.py

==============
Workflow steps
==============

Write your program
==================
Write your micropython program on your laptop. Here is a basic ``demo/hello-world/hello-world.py``::

    $ cat demo/hello-world/hello-world.py
    import hub
    from spikedev.motor import MotorSpeedDPS, SpikeMediumMotor

    print("Hello World")

    # Run the motor 720 degrees at 180 degrees-per-second
    mtr = SpikeMediumMotor(hub.port.E)
    mtr.run_for_degrees(720, MotorSpeedDPS(180))
    $

Run your program
================
Use the `ampy` tool to run ``demo/hello-world/hello-world.py``::

    $ sudo ampy --port /dev/ttyACM0 run demo/hello-world/hello-world.py