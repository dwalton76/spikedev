# spikedev libraries
# standard libraries
import sys

import utime
from spikedev.logging import log_msg
from util.sensors import get_sensor_value

MAXINT = sys.maxsize
MININT = MAXINT * -1


BUSY_MODE = 0
BUSY_SENSOR = 0
BUSY_MOTOR = 1


class MotorStop:
    FLOAT = 0
    BRAKE = 1
    HOLD = 2


class MotorCallbackEvent:
    COMPLETED = 0
    INTERRUPTED = 1
    STALL = 2


class MotorPolarity:
    NORMAL = 0
    REVERSED = 1


class MotorBase:
    def _event_callback(self, reason):
        if reason == MotorCallbackEvent.COMPLETED:
            self.interrupted = False
            self.stalled = False
        elif reason == MotorCallbackEvent.INTERRUPTED:
            self.interrupted = True
            self.stalled = False
        elif reason == MotorCallbackEvent.STALL:
            self.interrupted = False
            self.stalled = True
        else:
            raise ValueError("invalid callback reason {}" % (reason))

        self.rxed_callback = True

    def _wait(self):
        # This is ugly but SPIKE does not have the _thread module :(
        while not self.rxed_callback:
            utime.sleep(0.01)

    def _validate_degrees(self, degrees):
        if degrees < MININT or degrees > MAXINT:
            raise ValueError("degrees{} is invalid, must be between {} and {} (inclusive)" % (degrees, MININT, MAXINT))

    def _validate_speed(self, speed):
        if speed < -100 or speed > 100:
            raise ValueError("speed {} is invalid, must be between -100 and 100 (inclusive)" % (speed))

    def _validate_max_power(self, max_power):
        if max_power < 0 or max_power > 100:
            raise ValueError("max_power {} is invalid, must be between 0 and 100 (inclusive)" % (max_power))

    def _validate_stop(self, stop):
        if stop not in (MotorStop.FLOAT, MotorStop.BRAKE, MotorStop.HOLD):
            raise ValueError(
                "stop {} is invalid, must be one of %s, %s, %s"
                % (stop, MotorStop.FLOAT, MotorStop.BRAKE, MotorStop.HOLD)
            )

    def _validate_acceleration(self, acceleration):
        if acceleration < 0 or acceleration > 10000:
            raise ValueError("acceleration {} is invalid, must be between 0 and 10000 (inclusive)" % (acceleration))

    def _validate_deceleration(self, deceleration):
        if deceleration < 0 or deceleration > 10000:
            raise ValueError("deceleration {} is invalid, must be between 0 and 10000 (inclusive)" % (deceleration))

    def _validate_stall(self, stall):
        if stall not in (True, False):
            raise ValueError("stall {} is invalid, must be True or False" % (stall))

    def _validate_args(self, kwargs):

        for (keyword, value) in kwargs.items():

            if keyword == "speed":
                self._validate_speed(value)

            elif keyword == "degrees":
                self._validate_degrees(value)

            elif keyword == "max_power":
                self._validate_max_power(value)

            elif keyword == "stop":
                self._validate_stop(value)

            elif keyword == "acceleration":
                self._validate_acceleration(value)

            elif keyword == "deceleration":
                self._validate_deceleration(value)

            elif keyword == "stall":
                self._validate_stall(value)


class Motor(MotorBase):
    def __init__(self, port, polarity=MotorPolarity.NORMAL):
        super().__init__()
        self.port = port
        self.port_letter = str(port)[-2]
        self.interrupted = False
        self.stalled = False
        self.polarity = polarity

        # wait for motor to connect
        while self.port.motor is None:
            utime.sleep(0.1)

        self.port.motor.callback(self._event_callback)

    def __str__(self):
        return "%s(port %s)" % (self.__class__.__name__, self.port_letter)

    @property
    def position(self):
        return get_sensor_value(self.port_letter, 3, 0, (49, 48))

    @position.setter
    def position(self, value):
        """
        Set the motor encoder position to `value`
        """
        self.port.motor.preset(value)

    @property
    def is_stalled(self):
        return self.stalled

    @property
    def is_running(self):
        return bool(self.port.motor.busy(BUSY_MOTOR))

    def _number_with_polarity(self, value):
        if self.polarity == MotorPolarity.NORMAL:
            return value
        elif self.polarity == MotorPolarity.REVERSED:
            return value * -1
        else:
            raise ValueError("%s invalid polarity %s" % (self, self.polarity))

    def _degrees_with_polarity(self, degrees):
        return self._number_with_polarity(degrees)

    def _speed_with_polarity(self, speed):
        return self._number_with_polarity(speed)

    def run_at_speed(self, speed, max_power=0, acceleration=100, deceleration=150, stall=True):
        self.port.motor.run_at_speed(
            self._speed_with_polarity(speed),
            max_power=max_power,
            acceleration=acceleration,
            deceleration=deceleration,
            stall=stall,
        )

    def run_for_degrees(
        self,
        degrees,
        speed,
        max_power=0,
        stop=MotorStop.BRAKE,
        acceleration=100,
        deceleration=150,
        stall=True,
        block=True,
    ):
        log_msg("%s: run_for_degrees %s at speed %s" % (self, degrees, speed))
        self.rxed_callback = False
        self.port.motor.run_for_degrees(
            degrees=self._degrees_with_polarity(degrees),
            speed=speed,
            max_power=max_power,
            stop=stop,
            acceleration=acceleration,
            deceleration=deceleration,
            stall=stall,
        )

        if block:
            self._wait()

    def run_to_position(
        self,
        position,
        speed,
        max_power=0,
        stop=MotorStop.BRAKE,
        acceleration=100,
        deceleration=150,
        stall=True,
        block=True,
    ):
        log_msg("%s: run_to_position %s at speed %s" % (self, position, speed))
        self.rxed_callback = False
        self.port.motor.run_to_position(
            position=position,
            speed=speed,
            max_power=max_power,
            stop=stop,
            acceleration=acceleration,
            deceleration=deceleration,
            stall=stall,
        )

        if block:
            self._wait()

    def run_for_time(
        self, msec, speed, max_power=0, stop=MotorStop.BRAKE, acceleration=100, deceleration=150, stall=True, block=True
    ):
        log_msg("%s: run_for_time %sms at speed %s" % (self, msec, speed))
        self.rxed_callback = False
        self.port.motor.run_for_time(msec, speed, max_power, stop, acceleration, deceleration, stall)

        if block:
            self._wait()

    def stop(self, degrees, speed):
        pass


class MediumMotor(Motor):
    def __str__(self):
        return "MediumMotor(port %s)" % self.port_letter


class LargeMotor(Motor):
    def __str__(self):
        return "LargeMotor(port %s)" % self.port_letter


class MoveTank(MotorBase):
    def __init__(
        self,
        left_motor_port,
        right_motor_port,
        motor_class=MediumMotor,
        left_motor_polarity=MotorPolarity.REVERSED,
        right_motor_polarity=MotorPolarity.NORMAL,
    ):
        super().__init__()
        self.left_motor = motor_class(left_motor_port, left_motor_polarity)
        self.right_motor = motor_class(right_motor_port, right_motor_polarity)
        self.interrupted = False
        self.stalled = False
        self.pair = self.left_motor.port.motor.pair(self.right_motor.port.motor)
        self.pair.callback(self._event_callback)

    def __str__(self):
        return self.__class__.__name__

    def _speed_with_polarity(self, left_speed, right_speed):
        if self.left_motor.polarity == MotorPolarity.NORMAL:
            pass
        elif self.left_motor.polarity == MotorPolarity.REVERSED:
            left_speed *= -1
        else:
            raise ValueError("%s invalid polarity %s" % (self, self.left_motor.polarity))

        if self.right_motor.polarity == MotorPolarity.NORMAL:
            pass
        elif self.right_motor.polarity == MotorPolarity.REVERSED:
            right_speed *= -1
        else:
            raise ValueError("%s invalid polarity %s" % (self, self.right_motor.polarity))

        return (left_speed, right_speed)

    def run_at_speed(self, left_speed, right_speed, max_power=0, acceleration=100, deceleration=150):
        (left_speed, right_speed) = self._speed_with_polarity(left_speed, right_speed)
        self.pair.run_at_speed(
            left_speed,
            right_speed,
            max_power=max_power,
            acceleration=acceleration,
            deceleration=deceleration,
        )

    def run_for_degrees(
        self,
        degrees,
        left_speed,
        right_speed,
        max_power=0,
        stop=MotorStop.BRAKE,
        acceleration=100,
        deceleration=150,
        block=True,
    ):
        log_msg("%s: run_for_degrees %s at left_speed %s, right_speed %s" % (self, degrees, left_speed, right_speed))
        self.rxed_callback = False
        (left_speed, right_speed) = self._speed_with_polarity(left_speed, right_speed)
        self.pair.run_for_degrees(
            degrees,
            left_speed,
            right_speed,
            max_power=max_power,
            stop=stop,
            acceleration=acceleration,
            deceleration=deceleration,
        )

        if block:
            self._wait()

    def run_to_position(
        self,
        left_position,
        right_position,
        speed,
        max_power=0,
        stop=MotorStop.BRAKE,
        acceleration=100,
        deceleration=150,
        block=True,
    ):
        log_msg(
            "%s: run_to_position left_position %s, right_position %s, at speed %s"
            % (self, left_position, right_position, speed)
        )
        self.rxed_callback = False
        self.pair.run_to_position(
            left_position,
            right_position,
            speed,
            max_power=max_power,
            stop=stop,
            acceleration=acceleration,
            deceleration=deceleration,
        )

        if block:
            self._wait()

    def run_for_time(
        self,
        msec,
        left_speed,
        right_speed,
        max_power=0,
        stop=MotorStop.BRAKE,
        acceleration=100,
        deceleration=150,
        block=True,
    ):
        log_msg("%s: run_for_time %sms at left_speed %s, right_speed %s" % (self, msec, left_speed, right_speed))
        self.rxed_callback = False
        (left_speed, right_speed) = self._speed_with_polarity(left_speed, right_speed)
        self.pair.run_for_time(
            msec,
            left_speed,
            right_speed,
            max_power=max_power,
            stop=stop,
            acceleration=acceleration,
            deceleration=deceleration,
        )

        if block:
            self._wait()
