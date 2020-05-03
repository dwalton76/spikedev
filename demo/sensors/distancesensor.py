# standard libraries
import utime

# third party libraries
import hub

# spikedev libraries
from spikedev.logging import log_msg
from spikedev.sensor import DistanceSensor, DistanceSensorMode

log_msg("start")
ds = DistanceSensor(hub.port.A, mode=DistanceSensorMode.DISTL)

for x in range(10):
    log_msg(ds.value())
    utime.sleep(0.1)

log_msg("finish")
