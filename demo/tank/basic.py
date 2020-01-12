# spikedev libraries
import hub
from spikedev.motor import Motor

mtr = Motor(hub.port.E)
mtr.run_for_degrees(45, 10)
