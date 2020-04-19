# standard libraries
import utime

# third party libraries
import hub

utime.sleep(2)

for port in (hub.port.A, hub.port.B, hub.port.C, hub.port.D, hub.port.E, hub.port.F):
    if port.motor:
        port.motor.brake()
