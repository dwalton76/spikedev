# spikedev libraries
import hub
import utime
from spikedev.logging import log_msg
from spikedev.motor import MotorStop, MoveTank, SpeedDPS, SpeedRPM, SpikeMediumMotor

"""
mtr = SpikeMediumMotor(hub.port.E)
# mtr.run_for_degrees(360, 30)
mtr.run_for_time(6000, SpeedDPS(360))
#mtr.run_at_speed(SpeedRPM(10))
#utime.sleep(10)
#mtr.stop(MotorStop.BRAKE)

"""
tank = MoveTank(hub.port.E, hub.port.F)
# tank.run_for_degrees(360, 50, 50)
tank.run_for_time(3000, SpeedDPS(180), SpeedDPS(360))
tank.stop()
