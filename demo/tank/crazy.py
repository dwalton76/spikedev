# third party libraries
import hub

# spikedev libraries
from spikedev.motor import SpikeMediumMotor
# from spikedev.tank import MoveTank, MoveSteering
# from spikedev.wheel import SpikeWheel

mtr = SpikeMediumMotor(hub.port.E)
mtr.run_for_degrees(360, 40)