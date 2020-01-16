# spikedev
A micropython library for [LEGO SPIKE](https://education.lego.com/en-us/products/lego-education-spike-prime-set/45678#product). The goal of this library is to bring much of the work done at [ev3dev-lang-python](https://github.com/ev3dev/ev3dev-lang-python) to SPIKE.

# Installing spikedev
## ampy
Install [ampy](https://learn.adafruit.com/micropython-basics-load-files-and-run-code/install-ampy) on your laptop. We will use ampy to communicate with the SPIKE hub via
its usb port.

```bash
$ sudo pip3 install adafruit-ampy
```

## Booting SPIKE
The SPIKE UI (heart picture, click left/right to select a program, etc) is produced by a program called `main.py` that runs when the hub boots. We need to boot the SPIKE hub so
that `main.py` does not run (long story).

To do this hold down the left button when you press the big circle button to boot SPIKE.
You will not see the heart picture or hear the familiar chime, that is expected. You should
however see the circle button turn white.

## Copy spikedev files
We need to create a `spikedev` directory on SPIKE and copy all of our files to that
directory. To do that run:
```bash
$ sudo make install
```

# Workflow steps
## Write your program
Write your micropython program on your laptop. Here is a basic hello-world.py
```micropython
import hub
from spikedev.motor import MotorSpeedDPS, SpikeMediumMotor

print("Hello World")

# Run the motor 720 degrees at 180 degrees-per-second
mtr = SpikeMediumMotor(hub.port.E)
mtr.run_for_degrees(720, MotorSpeedDPS(180))
```

## Run your program
Use the `ampy` tool to run hello-world.py
```bash
$ sudo ampy --port /dev/ttyACM0 run demo/hello-world/hello-world.py
```
