# third party libraries
import hub

# spikedev libraries
from spikedev.motor import SpikeMediumMotor
from spikedev.tank import MoveTank, MoveSteering

mtr = SpikeMediumMotor(hub.port.A)
mtr.run_for_degrees(360, 40, stall=True)
