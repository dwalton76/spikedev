# third party libraries
import hub

# spikedev libraries
from spikedev.logging import log_msg
from spikedev.sensor import TouchSensor, TouchSensorMode

log_msg("start")
ts = TouchSensor(hub.port.B, mode=TouchSensorMode.TOUCH)
ts.wait_for_bump(5000)
log_msg("finish")
