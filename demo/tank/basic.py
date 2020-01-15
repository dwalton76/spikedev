# spikedev libraries
import hub
import utime
from spikedev.logging import log_msg
from spikedev.motor import MediumMotor, MotorStop, MoveTank

mtr = MediumMotor(hub.port.E)
# mtr.run_for_degrees(360, 30)
# mtr.run_for_time(3000, 50, block=False)
mtr.run_at_speed(30)
log_msg(mtr.position)
utime.sleep(4)
log_msg(mtr.position)
mtr.stop(MotorStop.BRAKE)

"""
tank = MoveTank(hub.port.E, hub.port.F)
#tank.run_for_degrees(360, 50, 50)
tank.run_for_time(3000, 20, 40)
tank.stop()
"""
