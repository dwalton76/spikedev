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
import utime

# spikedev libraries
from spikedev.logging import log_msg
from spikedev.motor import _callback  # noqa: F401
from spikedev.motor import _portletter2motor  # noqa: F401
from spikedev.motor import (
    MotorPolarity,
    MotorSpeed,
    MotorSpeedPercent,
    MotorStop,
    SpikeMediumMotor,
    _callback_A,
    _callback_B,
    _callback_C,
    _callback_D,
    _callback_E,
    _callback_F,
)
from spikedev.unit import distance_in_mm


class MoveTank:
    """
    .. image:: images/tank.png

    A class for supporting tank style robots that are driven by two motors

    Args:
        left_motor_port (str): port letter of the left motor
        right_motor_port (str): port letter of the right motor
        motor_class (Motor): the type of motor that is used, defaults to :class:`SpikeMediumMotor`
        left_motor_polarity (MotorPolarity): the polarity for the left motor, defaults
            to :class:`MotorPolarity.REVERSED`
        right_motor_polarity (MotorPolarity): the polarity for the right motor, defaults
            to :class:`MotorPolarity.NORMAL`
        desc (str): defaults to None

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MotorSpeedDPS
        from spikedev.tank import MoveTank

        tank = MoveTank(hub.port.E, hub.port.F)
        tank.run_for_time(3000, MotorSpeedDPS(180), MotorSpeedDPS(360))
    """

    def __init__(
        self,
        left_motor_port,
        right_motor_port,
        motor_class=SpikeMediumMotor,
        left_motor_polarity=MotorPolarity.REVERSED,
        right_motor_polarity=MotorPolarity.NORMAL,
        desc=None,
    ):
        super().__init__()
        self.left_motor = motor_class(left_motor_port, polarity=left_motor_polarity)
        self.right_motor = motor_class(right_motor_port, polarity=right_motor_polarity)
        self.interrupted = False
        self.stalled = False
        self.pair = self.left_motor.port.motor.pair(self.right_motor.port.motor)
        self.desc = None
        self.rxed_callback = True

        # callback setup
        if self.left_motor.port_letter == "A":
            self.pair.callback(_callback_A)
        elif self.left_motor.port_letter == "B":
            self.pair.callback(_callback_B)
        elif self.left_motor.port_letter == "C":
            self.pair.callback(_callback_C)
        elif self.left_motor.port_letter == "D":
            self.pair.callback(_callback_D)
        elif self.left_motor.port_letter == "E":
            self.pair.callback(_callback_E)
        elif self.left_motor.port_letter == "F":
            self.pair.callback(_callback_F)
        else:
            raise ValueError("invalid port {}".format(self.port_letter))

        global _portletter2motor
        _portletter2motor[self.left_motor.port_letter] = self

    def __str__(self):
        if self.desc is not None:
            return self.desc
        else:
            return self.__class__.__name__

    def _wait(self):
        # This is ugly but SPIKE does not have the _thread module :(
        while not self.rxed_callback:
            utime.sleep(0.01)

    def _speed_percentage(self, speed):

        if isinstance(speed, MotorSpeed):
            return speed.to_native_units(self.left_motor)

        # If speed is not a MotorSpeed object we treat it as a percentage
        else:
            return MotorSpeedPercent(speed).to_native_units(self.left_motor)

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
        """
        Stop both motors
        """
        self.pair.brake()

    def run_at_speed(self, left_speed, right_speed, **kwargs):
        """
        Run the motors at the specified speeds. The motors will run until you call ``stop()``

        Args:
            left_speed (MotorSpeed): the speed of the left motor
            right_speed (MotorSpeed): the speed of the right motor
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """
        left_speed = self._speed_percentage(left_speed)
        right_speed = self._speed_percentage(right_speed)
        (left_speed, right_speed) = self._speed_with_polarity(left_speed, right_speed)
        self.pair.run_at_speed(left_speed, right_speed, **kwargs)

    def run_for_degrees(self, degrees, left_speed, right_speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Run the motors at the specified speeds, the two motors combined will move an average of ``degrees``

        Args:
            degrees (int): the average number of degrees for the two motors to move
            left_speed (MotorSpeed): the speed of the left motor
            right_speed (MotorSpeed): the speed of the right motor
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """
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
        """
        Run both motors at ``speed`` to the desired positions

        Args:
            left_position (int): the target position for the left motor
            right_position (int): the target position for the right motor
            speed (MotorSpeed): the speed of both motors
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """
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
        """
        Run the motors at the specified speeds for ``msec``

        Args:
            msec (int): the number of milliseconds to run the motors
            left_speed (MotorSpeed): the speed of the left motor
            right_speed (MotorSpeed): the speed of the right motor
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """

        """
        rxed_callback = False

        def local_callback(reason):
            rxed_callback = True
            log_msg("rxed callback with reason {}".format(reason))

        if block:
            self.pair.callback(local_callback)
        else:
            self.pair.callback(None)
        """

        log_msg("{}: run_for_time {}ms at left_speed {}, right_speed {}".format(self, msec, left_speed, right_speed))
        left_speed = self._speed_percentage(left_speed)
        right_speed = self._speed_percentage(right_speed)
        (left_speed, right_speed) = self._speed_with_polarity(left_speed, right_speed)
        self.rxed_callback = False
        self.pair.run_for_time(msec, left_speed, right_speed, stop=stop, **kwargs)

        if block:
            self._wait()


class MoveSteering(MoveTank):
    """
    .. image:: images/steering.jpg

    MoveSteering is a child of :class:`MoveTank` that adds the ability to control the tank
    via a ``steering`` value and a ``speed`` value.

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MotorSpeedDPS
        from spikedev.tank import MoveSteering

        ms = MoveSteering(hub.port.E, hub.port.F)

        # Move forward and to the right for 500 degrees
        ms.run_for_degrees(500, 60, MotorSpeedDPS(180))
    """

    def _get_speed_steering(self, steering, speed):
        """
        Calculate the speed_sp for each motor in a pair to achieve the specified steering
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
        Run the motors according to the provided ``steering`` at ``speed``
        The motors will run until you call ``stop()``

        ``steering`` details:
            * -100 means turn left on the spot (right motor at 100% forward, left motor at 100% backward),
            *  0   means drive in a straight line, and
            *  100 means turn right on the spot (left motor at 100% forward, right motor at 100% backward).

        Args:
            steering (int): a number from -100 to 100
            speed (SpeedValue): The speed that should be applied to the outmost motor (the one rotating faster).
                The speed of the other motor will be computed automatically.
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """
        (left_speed, right_speed) = self._get_speed_steering(steering, speed)
        MoveTank.run_at_speed(self, left_speed, right_speed, **kwargs)

    def run_for_degrees(self, steering, speed, degrees, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Rotate the motors according to the provided ``steering`` at ``speed`` where the outmost motor (the
        one rotating faster) will move for ``degrees``.

        ``steering`` details:
            * -100 means turn left on the spot (right motor at 100% forward, left motor at 100% backward),
            *  0   means drive in a straight line, and
            *  100 means turn right on the spot (left motor at 100% forward, right motor at 100% backward).

        Args:
            steering (int): a number from -100 to 100
            speed (SpeedValue): The speed that should be applied to the outmost motor (the one rotating faster).
                The speed of the other motor will be computed automatically.
            degrees (int): the number of degrees for the outmost motor (the one rotating faster) to move
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """
        (left_speed, right_speed) = self._get_speed_steering(steering, speed)
        MoveTank.run_for_degrees(self, degrees, left_speed, right_speed, stop=stop, block=block, **kwargs)

    def run_for_time(self, msec, steering, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Rotate the motors according to the provided ``steering`` for ``seconds``.

        ``steering`` details:
            * -100 means turn left on the spot (right motor at 100% forward, left motor at 100% backward),
            *  0   means drive in a straight line, and
            *  100 means turn right on the spot (left motor at 100% forward, right motor at 100% backward).

        Args:
            msec (int): the number of milliseconds to run the motors
            steering (int): a number from -100 to 100
            speed (SpeedValue): The speed that should be applied to the outmost motor (the one rotating faster).
                The speed of the other motor will be computed automatically.
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """
        (left_speed, right_speed) = self._get_speed_steering(steering, speed)
        MoveTank.run_for_time(self, msec, left_speed, right_speed, stop=stop, block=block, **kwargs)


class MoveDifferential(MoveTank):
    """
    .. image:: images/differential.jpg

    MoveDifferential is a child of :class:`MoveTank` that adds the following capabilities:
        * drive in a straight line for a specified distance
        * rotate in place in a circle (clockwise or counter clockwise) for a specified number of degrees
        * drive in an arc (clockwise or counter clockwise) of a specified radius for a specified distance

    All of the args from MoveTank apply plus two additional args:

    Args:
        wheel_class (Wheel): used to get the circumference of the wheels of the robot. The
            circumference is needed for several calculations in this class.
        wheel_distance_mm (DistanceValue): The distance between the mid point of the two
            wheels of the robot. You may need to do some test drives to find
            the correct value for your robot.  It is not as simple as measuring
            the distance between the midpoints of the two wheels. The weight of
            the robot, center of gravity, etc come into play.

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MotorSpeedDPS
        from spikedev.tank import MoveDifferential
        from spikedev.unit import DistanceInches, DistanceStuds
        from spikedev.wheel import SpikeWheel

        md = MoveDifferential(hub.port.E, hub.port.F, SpikeWheel, DistanceStuds(11))

        # rotate 90 degrees clockwise
        md.turn_right(90, MotorSpeedDPS(100))

        # rotate 90 degrees counter-clockwise
        md.turn_left(90, MotorSpeedDPS(100))

        # drive forward 6 inches
        md.run_for_distance(DistanceInches(6), MotorSpeedDPS(100))

        # Drive in arc to the right along an imaginary circle of radius 12 inches.
        # Drive for 6 inches around this imaginary circle.
        md.run_arc_right(DistanceInches(12), DistanceInches(6), MotorSpeedDPS(100))
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

        Args:
            distance (DistanceValue): how far the midpoint between the wheels should travel
            speed (MotorSpeed): how fast the midpoint between the wheels should travel
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
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
        # circle_middle_mm = 2 * math.pi * radius_mm
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

        avg_wheel_rotations = float(distance_mm / self.wheel.circumference_mm)
        avg_wheel_degrees = int(avg_wheel_rotations * 360)
        log_msg(
            "{}: arc {}, radius {}, distance {}, left-speed {}, right-speed {}, ".format(
                self, "right" if arc_right else "left", radius_mm, distance_mm, left_speed, right_speed
            )
            + "wheel circumference_mm {}, avg_wheel_rotations {}, avg_wheel_degrees {}".format(
                self.wheel.circumference_mm, avg_wheel_rotations, avg_wheel_degrees
            )
        )

        MoveTank.run_for_degrees(self, avg_wheel_degrees, left_speed, right_speed, stop=stop, block=block, **kwargs)

    def run_arc_right(self, radius, distance, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Drive clockwise in a circle with ``radius`` for ``distance``

        Args:
            radius (DistanceValue): the radius of the arc to drive in, think of this as the size of
                the imaginary circle the robot will follow
            distance (DistanceValue): how far the midpoint between the wheels should travel along the imaginary circle
            speed (MotorSpeed): how fast the midpoint between the wheels should travel
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """
        radius_mm = distance_in_mm(radius)
        distance_mm = distance_in_mm(distance)
        self._run_arc(radius_mm, distance_mm, speed, stop, block, True, **kwargs)

    def run_arc_left(self, radius, distance, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Drive counter-clockwise in a circle with ``radius`` for ``distance``

        Args:
            radius (DistanceValue): the radius of the arc to drive in, think of this as the size of
                the imaginary circle the robot will follow
            distance (DistanceValue): how far the midpoint between the wheels should travel along the imaginary circle
            speed (MotorSpeed): how fast the midpoint between the wheels should travel
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """
        radius_mm = distance_in_mm(radius)
        distance_mm = distance_in_mm(distance)
        self._run_arc(radius_mm, distance_mm, speed, stop, block, False, **kwargs)

    def turn_degrees(self, degrees, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Rotate in place ``degrees``. Both wheels will turn at the same speed for us
        to rotate in place.

        Args:
            degrees (int): the number of degrees to rotate in place
            speed (MotorSpeed): how fast each wheel should move
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
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

    def turn_right(self, degrees, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Rotate clockwise ``degrees`` in place

        Args:
            degrees (int): the number of degrees to rotate clockwise in place
            speed (MotorSpeed): how fast each wheel should move
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """
        self.turn_degrees(abs(degrees), speed, stop, block, **kwargs)

    def turn_left(self, degrees, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Rotate counter-clockwise ``degrees`` in place

        Args:
            degrees (int): the number of degrees to rotate counter-clockwise in place
            speed (MotorSpeed): how fast each wheel should move
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """
        self.turn_degrees(abs(degrees) * -1, speed, stop, block, **kwargs)
