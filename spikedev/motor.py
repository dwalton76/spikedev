# Much of the code in this file was ported from ev3dev-lang-python so we
# are including the license for ev3dev-lang-python.

# -----------------------------------------------------------------------------
# Copyright (c) 2015 Ralph Hempel <rhempel@hempeldesigngroup.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------

# standard libraries
import math
import sys

# spikedev libraries
import utime
from spikedev.logging import log_msg
from spikedev.unit import distance_in_mm

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


class MotorMode:
    """
    for x in hub.port.E.info()["modes"]:
        print(x)
    """

    POWER = 0
    SPEED = 1
    POS = 2
    APOS = 3  # position but limited to -180 -> 180
    LOAD = 4
    CALIB = 5


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
            raise ValueError("invalid callback reason {}".format(reason))

        self.rxed_callback = True

    def _wait(self):
        # This is ugly but SPIKE does not have the _thread module :(
        while not self.rxed_callback:
            utime.sleep(0.01)

    def _validate_degrees(self, degrees):
        if degrees < MININT or degrees > MAXINT:
            raise ValueError(
                "degrees {} is invalid, must be between {} and {} (inclusive)".format(degrees, MININT, MAXINT)
            )

    def _validate_speed(self, speed):
        if speed < -100 or speed > 100:
            raise ValueError("speed {} is invalid, must be between -100 and 100 (inclusive)".format(speed))

    def _validate_max_power(self, max_power):
        if max_power < 0 or max_power > 100:
            raise ValueError("max_power {} is invalid, must be between 0 and 100 (inclusive)".format(max_power))

    def _validate_stop(self, stop):
        if stop not in (MotorStop.FLOAT, MotorStop.BRAKE, MotorStop.HOLD):
            raise ValueError(
                "stop {} is invalid, must be one of {}, {}, {}".format(
                    stop, MotorStop.FLOAT, MotorStop.BRAKE, MotorStop.HOLD
                )
            )

    def _validate_acceleration(self, acceleration):
        if acceleration < 0 or acceleration > 10000:
            raise ValueError("acceleration {} is invalid, must be between 0 and 10000 (inclusive)".format(acceleration))

    def _validate_deceleration(self, deceleration):
        if deceleration < 0 or deceleration > 10000:
            raise ValueError("deceleration {} is invalid, must be between 0 and 10000 (inclusive)".format(deceleration))

    def _validate_stall(self, stall):
        if stall not in (True, False):
            raise ValueError("stall {} is invalid, must be True or False".format(stall))

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
        self.port.motor.mode(MotorMode.POS)

    def __str__(self):
        return "{}(port {})".format(self.__class__.__name__, self.port_letter)

    def _speed_percentage(self, speed):

        if isinstance(speed, SpeedValue):
            return speed.to_native_units(self)

        # If speed is not a SpeedValue object we treat it as a percentage
        elif isinstance(speed, (float, int)):
            return SpeedPercent(speed).to_native_units(self)

        else:
            raise TypeError(type(speed))

    @property
    def position(self):
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
            raise ValueError("{} invalid polarity {}".format(self, self.polarity))

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
            raise ValueError("invalid stop_action {}".format(stop_action))

    def run_at_speed(self, speed, **kwargs):
        speed = self._speed_percentage(speed)
        self.port.motor.run_at_speed(self._speed_with_polarity(speed), **kwargs)

    def run_for_degrees(self, degrees, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        log_msg("{}: run_for_degrees {} at speed {}".format(self, degrees, speed))
        speed = self._speed_percentage(speed)
        self.rxed_callback = False
        self.port.motor.run_for_degrees(self._degrees_with_polarity(degrees), speed, stop=stop, **kwargs)

        if block:
            self._wait()

    def run_to_position(self, position, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        log_msg("{}: run_to_position {} at speed {}".format(self, position, speed))
        speed = self._speed_percentage(speed)
        self.rxed_callback = False
        self.port.motor.run_to_position(position, speed, stop=stop, **kwargs)

        if block:
            self._wait()

    def run_for_time(self, msec, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        log_msg("{}: run_for_time {}ms at speed {}".format(self, msec, speed))
        speed = self._speed_percentage(speed)
        self.rxed_callback = False
        self.port.motor.run_for_time(msec, speed, stop=stop, **kwargs)

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
        return "SpikeMediumMotor(port {})".format(self.port_letter)


class SpikeLargeMotor(Motor):
    """
    part number 45602
    """

    MAX_RPM = 175
    MAX_RPS = 2.916666
    MAX_DPM = 63000
    MAX_DPS = 1050

    def __str__(self):
        return "SpikeLargeMotor(port {})".format(self.port_letter)


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
            raise ValueError("{} invalid polarity {}".format(self, self.left_motor.polarity))

        if self.right_motor.polarity == MotorPolarity.NORMAL:
            pass
        elif self.right_motor.polarity == MotorPolarity.REVERSED:
            right_speed *= -1
        else:
            raise ValueError("{} invalid polarity {}".format(self, self.right_motor.polarity))

        return (left_speed, right_speed)

    def stop(self):
        self.pair.brake()

    def run_at_speed(self, left_speed, right_speed, **kwargs):
        left_speed = self._speed_percentage(left_speed)
        right_speed = self._speed_percentage(right_speed)
        (left_speed, right_speed) = self._speed_with_polarity(left_speed, right_speed)
        self.pair.run_at_speed(left_speed, right_speed, **kwargs)

    def run_for_degrees(self, degrees, left_speed, right_speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        log_msg(
            "{}: run_for_degrees {} at left_speed {}, right_speed {}".format(self, degrees, left_speed, right_speed)
        )
        left_speed = self._speed_percentage(left_speed)
        right_speed = self._speed_percentage(right_speed)
        self.rxed_callback = False
        (left_speed, right_speed) = self._speed_with_polarity(left_speed, right_speed)
        self.pair.run_for_degrees(degrees, left_speed, right_speed, stop=stop, **kwargs)

        if block:
            self._wait()

    def run_to_position(self, left_position, right_position, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        log_msg(
            "{}: run_to_position left_position {}, right_position {}, at speed {}".format(
                self, left_position, right_position, speed
            )
        )
        speed = self._speed_percentage(speed)
        self.rxed_callback = False
        self.pair.run_to_position(left_position, right_position, speed, stop=stop, **kwargs)

        if block:
            self._wait()

    def run_for_time(self, msec, left_speed, right_speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        log_msg("{}: run_for_time {}ms at left_speed {}, right_speed {}".format(self, msec, left_speed, right_speed))
        left_speed = self._speed_percentage(left_speed)
        right_speed = self._speed_percentage(right_speed)
        self.rxed_callback = False
        (left_speed, right_speed) = self._speed_with_polarity(left_speed, right_speed)
        self.pair.run_for_time(msec, left_speed, right_speed, stop=stop, **kwargs)

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

        import hub
        from spikedev.motor import MoveSteering, SpeedDPS

        ms = MoveSteering(hub.port.E, hub.port.F)
        ms.run_for_degrees(180, 80, SpeedDPS(180))
        ms.run_for_time(1000, -80, SpeedDPS(180))
    """

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

        speed = self._speed_percentage(speed)
        left_speed = speed
        right_speed = speed
        speed_factor = (50 - abs(float(steering))) / 50

        if steering >= 0:
            right_speed *= speed_factor
        else:
            left_speed *= speed_factor

        return (left_speed, right_speed)

    def run_at_speed(self, steering, speed, **kwargs):
        """
        Start rotating the motors according to the provided ``steering`` and
        ``speed`` forever.
        """
        (left_speed, right_speed) = self.get_speed_steering(steering, speed)
        MoveTank.run_at_speed(self, left_speed, right_speed, **kwargs)

    def run_for_degrees(self, steering, speed, degrees, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Rotate the motors according to the provided ``steering``.

        The distance each motor will travel follows the rules of :meth:`MoveTank.on_for_degrees`.
        """
        (left_speed, right_speed) = self.get_speed_steering(steering, speed)
        MoveTank.run_for_degrees(self, degrees, left_speed, right_speed, stop=stop, block=block, **kwargs)

    def run_for_time(self, msec, steering, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Rotate the motors according to the provided ``steering`` for ``seconds``.
        """
        (left_speed, right_speed) = self.get_speed_steering(steering, speed)
        MoveTank.run_for_time(self, msec, left_speed, right_speed, stop=stop, block=block, **kwargs)


class MoveDifferential(MoveTank):
    """
    MoveDifferential is a child of MoveTank that adds the following capabilities:

    - drive in a straight line for a specified distance

    - rotate in place in a circle (clockwise or counter clockwise) for a
      specified number of degrees

    - drive in an arc (clockwise or counter clockwise) of a specified radius
      for a specified distance

    New arguments:

    wheel_class - A child class of :class:`ev3dev2.wheel.Wheel`. This is used to
    get the circumference of the wheels of the robot. The circumference is
    needed for several calculations in this class.

    wheel_distance_mm - The distance between the mid point of the two
    wheels of the robot. You may need to do some test drives to find
    the correct value for your robot.  It is not as simple as measuring
    the distance between the midpoints of the two wheels. The weight of
    the robot, center of gravity, etc come into play.

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MoveDifferential, SpeedDPS
        from spikedev.unit import DistanceInches, DistanceStuds
        from spikedev.wheel import SpikeWheel

        md = MoveDifferential(hub.port.E, hub.port.F, SpikeWheel, DistanceStuds(11))

        # rotate 90 degrees clockwise
        md.turn_right(90, SpeedDPS(100))

        # rotate 90 degrees counter-clockwise
        md.turn_left(90, SpeedDPS(100))

        # drive forward 6 inches
        md.run_for_distance(DistanceInches(6), SpeedDPS(100))

        # Drive in arc to the right along an imaginary circle of radius 12 inches.
        # Drive for 6 inches around this imaginary circle.
        md.run_arc_right(DistanceInches(12), DistanceInches(6), SpeedDPS(100))
    """

    def __init__(
        self,
        left_motor_port,
        right_motor_port,
        wheel_class,  # an object from wheel.py
        wheel_distance,  # an int of mm or any DistanceValue object
        motor_class=SpikeMediumMotor,
        left_motor_polarity=MotorPolarity.REVERSED,
        right_motor_polarity=MotorPolarity.NORMAL,
    ):

        MoveTank.__init__(
            self,
            left_motor_port,
            right_motor_port,
            motor_class=motor_class,
            left_motor_polarity=left_motor_polarity,
            right_motor_polarity=right_motor_polarity,
        )

        self.wheel = wheel_class()
        self.wheel_distance_mm = distance_in_mm(wheel_distance)

        # The circumference of the circle made if this robot were to rotate in place
        self.circumference_mm = self.wheel_distance_mm * math.pi

        self.min_circle_radius_mm = self.wheel_distance_mm / 2

    def run_for_distance(self, distance, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Drive in a straight line for ``distance``
        """
        distance_mm = distance_in_mm(distance)
        rotations = distance_mm / self.wheel.circumference_mm
        degrees = int(rotations * 360)
        log_msg(
            "{}: run_for_distance distance_mm {}, rotations {}, speed {}".format(self, distance_mm, rotations, speed)
        )
        MoveTank.run_for_degrees(self, degrees, speed, speed, stop=stop, block=block, **kwargs)

    def _run_arc(self, radius_mm, distance_mm, speed, stop, block, arc_right, **kwargs):
        """
        Drive in a circle with ``radius`` for ``distance``
        """
        if radius_mm < self.min_circle_radius_mm:
            raise ValueError(
                "{}: radius_mm {} is less than min_circle_radius_mm {}".format(
                    self, radius_mm, self.min_circle_radius_mm
                )
            )

        speed = self._speed_percentage(speed)

        # The circle formed at the halfway point between the two wheels is the
        # circle that must have a radius of radius_mm
        circle_outer_mm = 2 * math.pi * (radius_mm + (self.wheel_distance_mm / 2))
        circle_middle_mm = 2 * math.pi * radius_mm
        circle_inner_mm = 2 * math.pi * (radius_mm - (self.wheel_distance_mm / 2))

        if arc_right:
            # The left wheel is making the larger circle and will move at 'speed'
            # The right wheel is making a smaller circle so its speed will be a fraction of the left motor's speed
            left_speed = speed
            right_speed = float(circle_inner_mm / circle_outer_mm) * left_speed

        else:
            # The right wheel is making the larger circle and will move at 'speed'
            # The left wheel is making a smaller circle so its speed will be a fraction of the right motor's speed
            right_speed = speed
            left_speed = float(circle_inner_mm / circle_outer_mm) * right_speed

        log_msg(
            "{}: arc {}, radius {}, distance {}, left-speed {}, right-speed {}, ".format(
                self, "right" if arc_right else "left", radius_mm, distance_mm, left_speed, right_speed
            )
            + "circle_outer_mm {}, circle_middle_mm {}, circle_inner_mm {}".format(
                circle_outer_mm, circle_middle_mm, circle_inner_mm
            )
        )

        # We know we want the middle circle to be of length distance_mm so
        # calculate the percentage of circle_middle_mm we must travel for the
        # middle of the robot to travel distance_mm.
        circle_middle_percentage = float(distance_mm / circle_middle_mm)

        # Now multiple that percentage by circle_outer_mm to calculate how
        # many mm the outer wheel should travel.
        circle_outer_final_mm = circle_middle_percentage * circle_outer_mm

        outer_wheel_rotations = float(circle_outer_final_mm / self.wheel.circumference_mm)
        outer_wheel_degrees = int(outer_wheel_rotations * 360)

        log_msg(
            "{}: arc {}, circle_middle_percentage {}, circle_outer_final_mm {}, ".format(
                self, "right" if arc_right else "left", circle_middle_percentage, circle_outer_final_mm
            )
            + "outer_wheel_rotations {}, outer_wheel_degrees {}".format(outer_wheel_rotations, outer_wheel_degrees)
        )

        MoveTank.run_for_degrees(self, outer_wheel_degrees, left_speed, right_speed, stop=stop, block=block, **kwargs)

    def run_arc_right(self, radius, distance, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Drive clockwise in a circle with ``radius`` for ``distance``
        """
        radius_mm = distance_in_mm(radius)
        distance_mm = distance_in_mm(distance)
        self._run_arc(radius_mm, distance_mm, speed, stop, block, True, **kwargs)

    def run_arc_left(self, radius, distance, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Drive counter-clockwise in a circle with ``radius`` for ``distance``
        """
        radius_mm = distance_in_mm(radius)
        distance_mm = distance_in_mm(distance)
        self._run_arc(radius_mm, distance_mm, speed, stop, block, False, **kwargs)

    def turn_degrees(self, degrees, speed, stop=MotorStop.BRAKE, block=True, error_margin=2, use_gyro=False, **kwargs):
        """
        Rotate in place ``degrees``. Both wheels must turn at the same speed for us
        to rotate in place.  If the following conditions are met the GryoSensor will
        be used to improve the accuracy of our turn:
        - ``use_gyro``, ``brake`` and ``block`` are all True
        - A GyroSensor has been defined via ``self.gyro = GyroSensor()``
        """

        """
        def final_angle(init_angle, degrees):
            result = init_angle - degrees

            while result <= -360:
                result += 360

            while result >= 360:
                result -= 360

            if result < 0:
                result += 360

            return result

        # use the gyro to check that we turned the correct amount?
        use_gyro = bool(use_gyro and block and stop in (MotorStop.BRAKE, MotorStop.HOLD) and self._gyro)

        if use_gyro:
            angle_init_degrees = self._gyro.circle_angle()
        else:
            angle_init_degrees = math.degrees(self.theta)

        angle_target_degrees = final_angle(angle_init_degrees, degrees)

        log_msg(
            "{}: turn_degrees() {} degrees from {} to {}".format(
                self, degrees, angle_init_degrees, angle_target_degrees
            )
        )
        """

        # The distance each wheel needs to travel
        distance_mm = (degrees * self.circumference_mm) / 360

        # The number of rotations to move distance_mm
        rotations = distance_mm / self.wheel.circumference_mm
        degrees = int(rotations * 360)

        # If degrees is positive rotate clockwise
        if degrees > 0:
            MoveTank.run_for_degrees(self, degrees, speed, speed * -1, stop=stop, block=block, **kwargs)

        # If degrees is negative rotate counter-clockwise
        else:
            MoveTank.run_for_degrees(self, degrees, speed * -1, speed, stop=stop, block=block, **kwargs)

        """
        if use_gyro:
            angle_current_degrees = self._gyro.circle_angle()

            # This can happen if we are aiming for 2 degrees and overrotate to 358 degrees
            # We need to rotate counter-clockwise
            if 90 >= angle_target_degrees >= 0 and 270 <= angle_current_degrees <= 360:
                degrees_error = (angle_target_degrees + (360 - angle_current_degrees)) * -1

            # This can happen if we are aiming for 358 degrees and overrotate to 2 degrees
            # We need to rotate clockwise
            elif 360 >= angle_target_degrees >= 270 and 0 <= angle_current_degrees <= 90:
                degrees_error = angle_current_degrees + (360 - angle_target_degrees)

            # We need to rotate clockwise
            elif angle_current_degrees > angle_target_degrees:
                degrees_error = angle_current_degrees - angle_target_degrees

            # We need to rotate counter-clockwise
            else:
                degrees_error = (angle_target_degrees - angle_current_degrees) * -1

            log_msg(
                "{}: turn_degrees() ended up at {}, error {}, error_margin {}".format(
                    self, angle_current_degrees, degrees_error, error_margin
                )
            )

            if abs(degrees_error) > error_margin:
                self.turn_degrees(degrees_error, speed, stop, block, error_margin, use_gyro, **kwargs)
        """

    def turn_right(self, degrees, speed, stop=MotorStop.BRAKE, block=True, error_margin=2, use_gyro=False, **kwargs):
        """
        Rotate clockwise ``degrees`` in place
        """
        self.turn_degrees(abs(degrees), speed, stop, block, error_margin, use_gyro, **kwargs)

    def turn_left(self, degrees, speed, stop=MotorStop.BRAKE, block=True, error_margin=2, use_gyro=False, **kwargs):
        """
        Rotate counter-clockwise ``degrees`` in place
        """
        self.turn_degrees(abs(degrees) * -1, speed, stop, block, error_margin, use_gyro, **kwargs)
