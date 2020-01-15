# spikedev libraries
# standard libraries
import sys

import utime
from spikedev.logging import log_msg

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


class SpeedValue(object):
    """
    A base class for other unit types. Don't use this directly; instead, see
    :class:`SpeedPercent`, :class:`SpeedRPS`, :class:`SpeedRPM`,
    :class:`SpeedDPS`, and :class:`SpeedDPM`.
    """

    def __eq__(self, other):
        return self.to_native_units() == other.to_native_units()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.to_native_units() < other.to_native_units()

    def __le__(self, other):
        return self.to_native_units() <= other.to_native_units()

    def __gt__(self, other):
        return self.to_native_units() > other.to_native_units()

    def __ge__(self, other):
        return self.to_native_units() >= other.to_native_units()

    def __rmul__(self, other):
        return self.__mul__(other)


class SpeedPercent(SpeedValue):
    """
    Speed as a percentage of the motor's maximum rated speed
    """

    def __init__(self, percent):
        if percent < -100 or percent > 100:
            raise ValueError("{} is an invalid percentage, must be between -100 and 100 (inclusive)".format(percent))

        self.percent = int(percent)

    def __str__(self):
        return str(self.percent) + "%"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return SpeedPercent(self.percent * other)

    def to_native_units(self, motor):
        """
        The native unit for a Spike motor is speed percentage
        """
        return self.percent


class SpeedRPS(SpeedValue):
    """
    Speed in rotations-per-second
    """

    def __init__(self, rotations_per_second):
        self.rotations_per_second = rotations_per_second

    def __str__(self):
        return str(self.rotations_per_second) + " rot/sec"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return SpeedRPS(self.rotations_per_second * other)

    def to_native_units(self, motor):
        """
        Return the speed percentage required to achieve desired rotations-per-second
        """
        if abs(self.rotations_per_second) > motor.MAX_RPS:
            raise ValueError(
                "invalid rotations-per-second: {} max RPS is {}, {} was requested".format(
                    motor, motor.MAX_RPS, self.rotations_per_second
                )
            )
        return int((self.rotations_per_second / motor.MAX_RPS) * 100)


class SpeedRPM(SpeedValue):
    """
    Speed in rotations-per-minute
    """

    def __init__(self, rotations_per_minute):
        self.rotations_per_minute = rotations_per_minute

    def __str__(self):
        return str(self.rotations_per_minute) + " rot/min"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return SpeedRPM(self.rotations_per_minute * other)

    def to_native_units(self, motor):
        """
        Return the speed percentage required to achieve desired rotations-per-minute
        """
        if abs(self.rotations_per_minute) > motor.MAX_RPM:
            raise ValueError(
                "invalid rotations-per-minute: {} max RPM is {}, {} was requested".format(
                    motor, motor.MAX_RPM, self.rotations_per_minute
                )
            )
        return int((self.rotations_per_minute / motor.MAX_RPM) * 100)


class SpeedDPS(SpeedValue):
    """
    Speed in degrees-per-second
    """

    def __init__(self, degrees_per_second):
        self.degrees_per_second = degrees_per_second

    def __str__(self):
        return str(self.degrees_per_second) + " deg/sec"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return SpeedDPS(self.degrees_per_second * other)

    def to_native_units(self, motor):
        """
        Return the speed percentage required to achieve desired degrees-per-second
        """
        if abs(self.degrees_per_second) > motor.MAX_DPS:
            raise ValueError(
                "invalid degrees-per-second: {} max DPS is {}, {} was requested".format(
                    motor, motor.MAX_DPS, self.degrees_per_second
                )
            )
        return int((self.degrees_per_second / motor.MAX_DPS) * 100)


class SpeedDPM(SpeedValue):
    """
    Speed in degrees-per-minute
    """

    def __init__(self, degrees_per_minute):
        self.degrees_per_minute = degrees_per_minute

    def __str__(self):
        return str(self.degrees_per_minute) + " deg/min"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return SpeedDPM(self.degrees_per_minute * other)

    def to_native_units(self, motor):
        """
        Return the speed percentage required to achieve desired degrees-per-minute
        """
        if abs(self.degrees_per_minute) > motor.MAX_DPM:
            "invalid degrees-per-minute: {} max DPM is {}, {} was requested".format(
                motor, motor.MAX_DPM, self.degrees_per_minute
            )
        return int(self.degrees_per_minute / motor.MAX_DPM * motor.max_speed)


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

    def _speed_percentage(self, speed):

        if isinstance(speed, SpeedValue):
            return speed.to_native_units(self)

        # If speed is not a SpeedValue object we treat it as a percentage
        else:
            return SpeedPercent(speed).to_native_units(self)

    @property
    def position(self):
        # HMMM this is how it is done in the scratch->python translation
        # but this always returns 0.  Am not sure yet how to get the motor position.
        # from util.sensors import get_sensor_value
        # return get_sensor_value(self.port_letter, 3, 0, (49, 48))

        # This returns something but I don't know what it is...it isn't the position though
        return self.port.motor.get()

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

    def stop(self, stop_action=MotorStop.BRAKE):

        if stop_action == MotorStop.FLOAT:
            self.port.motor.float()

        elif stop_action == MotorStop.BRAKE:
            self.port.motor.brake()

        elif stop_action == MotorStop.HOLD:
            self.port.motor.hold()

        else:
            raise ValueError("invalid stop_action %s" % stop_action)

    def run_at_speed(self, speed, max_power=0, acceleration=100, deceleration=150, stall=True):
        speed = self._speed_percentage(speed)
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
        speed = self._speed_percentage(speed)
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
        speed = self._speed_percentage(speed)
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
        speed = self._speed_percentage(speed)
        self.rxed_callback = False
        self.port.motor.run_for_time(msec, speed, max_power, stop, acceleration, deceleration, stall)

        if block:
            self._wait()


class SpikeMediumMotor(Motor):
    """
    part number 45603
    """

    MAX_RPM = 135  # rotations per minute
    MAX_RPS = 2.25  # rotations per second
    MAX_DPM = 48600  # degrees per minute
    MAX_DPS = 810  # degrees per second

    def __str__(self):
        return "SpikeMediumMotor(port %s)" % self.port_letter


class SpikeLargeMotor(Motor):
    """
    part number 45602
    """

    MAX_RPM = 175
    MAX_RPS = 2.916666
    MAX_DPM = 63000
    MAX_DPS = 1050

    def __str__(self):
        return "SpikeLargeMotor(port %s)" % self.port_letter


class MoveTank(MotorBase):
    def __init__(
        self,
        left_motor_port,
        right_motor_port,
        motor_class=SpikeMediumMotor,
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

    def _speed_percentage(self, speed):

        if isinstance(speed, SpeedValue):
            return speed.to_native_units(self.left_motor)

        # If speed is not a SpeedValue object we treat it as a percentage
        else:
            return SpeedPercent(speed).to_native_units(self.left_motor)

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

    def stop(self):
        self.pair.brake()

    def run_at_speed(self, left_speed, right_speed, max_power=0, acceleration=100, deceleration=150):
        left_speed = self._speed_percentage(left_speed)
        right_speed = self._speed_percentage(right_speed)
        (left_speed, right_speed) = self._speed_with_polarity(left_speed, right_speed)
        self.pair.run_at_speed(
            left_speed, right_speed, max_power=max_power, acceleration=acceleration, deceleration=deceleration
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
        left_speed = self._speed_percentage(left_speed)
        right_speed = self._speed_percentage(right_speed)
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
        speed = self._speed_percentage(speed)
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
        left_speed = self._speed_percentage(left_speed)
        right_speed = self._speed_percentage(right_speed)
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


class MoveSteering(MoveTank):
    """
    Controls a pair of motors simultaneously, via a single "steering" value and a speed.

    steering [-100, 100]:
        * -100 means turn left on the spot (right motor at 100% forward, left motor at 100% backward),
        *  0   means drive in a straight line, and
        *  100 means turn right on the spot (left motor at 100% forward, right motor at 100% backward).

    "steering" can be any number between -100 and 100.

    Example:

    .. code:: python

        steering_drive = MoveSteering(OUTPUT_A, OUTPUT_B)
        # drive in a turn for 10 rotations of the outer motor
        steering_drive.on_for_rotations(-20, SpeedPercent(75), 10)
    """

    def run_at_speed(self, steering, speed, max_power=0, acceleration=100, deceleration=150):
        """
        Start rotating the motors according to the provided ``steering`` and
        ``speed`` forever.
        """
        (left_speed, right_speed) = self.get_speed_steering(steering, speed)
        MoveTank.run_at_speed(self, left_speed, right_speed, max_power, acceleration, deceleration)

    def run_for_degrees(
        self,
        steering,
        speed,
        degrees,
        max_power=0,
        stop=MotorStop.BRAKE,
        acceleration=100,
        deceleration=150,
        block=True,
    ):
        """
        Rotate the motors according to the provided ``steering``.

        The distance each motor will travel follows the rules of :meth:`MoveTank.on_for_degrees`.
        """
        (left_speed, right_speed) = self.get_speed_steering(steering, speed)
        MoveTank.run_for_degrees(
            self, degrees, left_speed, right_speed, max_power, stop, acceleration, deceleration, block
        )

    def run_for_time(
        self, msec, steering, speed, max_power=0, stop=MotorStop.BRAKE, acceleration=100, deceleration=150, block=True
    ):
        """
        Rotate the motors according to the provided ``steering`` for ``seconds``.
        """
        (left_speed, right_speed) = self.get_speed_steering(steering, speed)
        MoveTank.run_for_time(self, msec, left_speed, right_speed, max_power, stop, acceleration, deceleration, block)

    def get_speed_steering(self, steering, speed):
        """
        Calculate the speed_sp for each motor in a pair to achieve the specified
        steering. Note that calling this function alone will not make the
        motors move, it only calculates the speed. A run_* function must be called
        afterwards to make the motors move.

        steering [-100, 100]:
            * -100 means turn left on the spot (right motor at 100% forward, left motor at 100% backward),
            *  0   means drive in a straight line, and
            *  100 means turn right on the spot (left motor at 100% forward, right motor at 100% backward).

        speed:
            The speed that should be applied to the outmost motor (the one
            rotating faster). The speed of the other motor will be computed
            automatically.
        """

        if steering < -100 or steering > 100:
            raise ValueError("{} is an invalid steering, must be between -100 and 100 (inclusive)".format(steering))

        # We don't have a good way to make this generic for the pair... so we
        # assume that the left motor's speed stats are the same as the right
        # motor's.
        speed = self._speed_percentage(speed)
        left_speed = speed
        right_speed = speed
        speed_factor = (50 - abs(float(steering))) / 50

        if steering >= 0:
            right_speed *= speed_factor
        else:
            left_speed *= speed_factor

        return (left_speed, right_speed)
