# spikedev libraries
import hub
from spikedev.motor import MoveTank

# mtr = MediumMotor(hub.port.E)
# mtr.run_for_degrees(360, 30)

tank = MoveTank(hub.port.E, hub.port.F)
#tank.run_for_degrees(360, 50, 50)
tank.run_for_time(3000, 220, 50)
