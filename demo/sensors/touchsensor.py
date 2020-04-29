# third party libraries
import hub

# spikedev libraries
from spikedev.logging import log_msg
from spikedev.sensor import TouchSensor, TouchSensorMode

log_msg("start")
ts = TouchSensor(hub.port.B, mode=TouchSensorMode.TOUCH)
#ts.wait_for_pressed(5000)
ts.wait_for_bump(5000)

# for x in range(40):
#    log_msg(ts.value())
#    utime.sleep(0.1)

log_msg("finish")
