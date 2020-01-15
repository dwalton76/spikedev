import hub
from spikedev.motor import SpeedDPS, SpikeMediumMotor

print("Hello World")
mtr = SpikeMediumMotor(hub.port.E)
mtr.run_for_degrees(720, SpeedDPS(180))
