# spikedev libraries
import utime
from spikedev.logging import log_msg
from util.sensors import get_sensor_value


class Motor:
    def __init__(self, port):
        self.port = port
        self.port_letter = str(port)[-2]

        # wait for motor to connect
        while self.port.motor is None:
            utime.sleep(0.1)

    def __str__(self):
        return "Motor(port %s)" % self.port_letter

    def run_for_degrees(self, degrees, speed):
        log_msg("%s: run_for_degrees %s at speed %s, position %s" % (self, degrees, speed, self.position()))
        self.port.motor.run_for_degrees(degrees, speed)
        log_msg("%s: run_for_degrees, position %s" % (self, self.position()))

    def position(self):
        return get_sensor_value(self.port_letter, 3, 0, (49, 48))
