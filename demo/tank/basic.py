# spikedev libraries
import hub
import utime
from spikedev.logging import log_msg
from spikedev.motor import MotorStop, MoveTank, SpeedDPS, SpeedRPM, SpikeMediumMotor, MoveSteering

"""
mtr = SpikeMediumMotor(hub.port.E)
# mtr.run_for_degrees(360, 30)
mtr.run_for_time(6000, SpeedDPS(360))
#mtr.run_at_speed(SpeedRPM(10))
#utime.sleep(10)
#mtr.stop(MotorStop.BRAKE)
"""

"""
tank = MoveTank(hub.port.E, hub.port.F)
# tank.run_for_degrees(360, 50, 50)
tank.run_for_time(3000, SpeedDPS(180), SpeedDPS(360))
tank.stop()
"""


ms = MoveSteering(hub.port.E, hub.port.F)
#ms.run_at_speed(100, SpeedDPS(360))
#utime.sleep(3)
#ms.stop()
ms.run_for_degrees(100, SpeedDPS(360), 1080)
#ms.run_for_time(3000, 100, SpeedDPS(360))
