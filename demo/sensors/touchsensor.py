import utime

import hub

# spikedev libraries
from spikedev.sensor import TouchSensor
from spikedev.logging import log_msg

log_msg("start")
ts = TouchSensor(hub.port.B)

for x in range(100):
    log_msg(ts.value())
    utime.sleep(0.1)

log_msg("finish")
