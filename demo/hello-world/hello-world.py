# spikedev libraries
import hub
from spikedev.motor import SpeedDPS, SpikeMediumMotor

# Run the motor 720 degrees at 180 degrees-per-second
print("Hello World")
mtr = SpikeMediumMotor(hub.port.E)
mtr.run_for_degrees(720, SpeedDPS(180))
