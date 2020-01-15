import hub
from spikedev.motor import SpeedDPS, SpikeMediumMotor
from spikedev.unit import DistanceInches, DistanceStuds

print("Hello World")
mtr = SpikeMediumMotor(hub.port.E)
mtr.run_for_degrees(720, SpeedDPS(180))
