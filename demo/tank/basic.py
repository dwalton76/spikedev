# standard libraries
import utime

# third party libraries
import hub

# spikedev libraries
from spikedev.logging import log_msg
from spikedev.motor import MotorSpeedDPS, MotorSpeedRPM, MotorStop, SpikeMediumMotor
from spikedev.tank import MoveDifferential, MoveSteering, MoveTank
from spikedev.unit import DistanceInches, DistanceStuds
from spikedev.wheel import SpikeWheel

"""
mtr = SpikeMediumMotor(hub.port.E)
# mtr.run_for_degrees(360, 30)
mtr.run_for_time(6000, MotorSpeedDPS(360))
#mtr.run_at_speed(MotorSpeedRPM(10))
#utime.sleep(10)
#mtr.stop(MotorStop.BRAKE)
"""

"""
tank = MoveTank(hub.port.E, hub.port.F)
# tank.run_for_degrees(360, 50, 50)
tank.run_for_time(3000, MotorSpeedDPS(180), MotorSpeedDPS(360))
tank.stop()
"""

"""
ms = MoveSteering(hub.port.E, hub.port.F)
# ms.run_at_speed(100, MotorSpeedDPS(360))
# utime.sleep(3)
# ms.stop()
# ms.run_for_degrees(180, 100, MotorSpeedDPS(180))
ms.run_for_time(1000, -100, MotorSpeedDPS(180))
"""

md = MoveDifferential(hub.port.E, hub.port.F, SpikeWheel, DistanceStuds(11))
# md.turn_right(90, MotorSpeedDPS(100))
# md.turn_left(90, MotorSpeedDPS(100))
# md.run_for_distance(DistanceInches(6), MotorSpeedDPS(100))
# md.run_arc_right(DistanceInches(12), DistanceInches(6), MotorSpeedDPS(100))
md.run_arc_left(DistanceInches(12), DistanceInches(6), MotorSpeedDPS(100))
