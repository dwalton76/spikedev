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
import utime

# spikedev libraries
from spikedev.logging import log_msg

MAXINT = 2147483648
MININT = MAXINT * -1

BUSY_MODE = 0
BUSY_SENSOR = 0
BUSY_MOTOR = 1


class MotorSpeed:
    """
    A base class for ``MotorSpeed`` classes. Do not use this directly. Use one of:

    * :class:`MotorSpeedPercent`
    * :class:`MotorSpeedRPS`
    * :class:`MotorSpeedRPM`
    * :class:`MotorSpeedDPS`
    * :class:`MotorSpeedDPM`
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


class MotorSpeedPercent(MotorSpeed):
    """
    Motor speed as a percentage of the motor's maximum rated speed

    Args:
        percent (int): the speed percentage to store

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MotorSpeedPercent, SpikeMediumMotor

        # run for 720 degrees at 40% of motor's maximum speed
        mtr = SpikeMediumMotor(hub.port.E)
        mtr.run_for_degrees(720, MotorSpeedPercent(40))
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
        return MotorSpeedPercent(self.percent * other)

    def to_native_units(self, motor):
        """
        The native unit for a Spike motor is speed percentage so there is nothing to adjust here

        Args:
            motor (Motor): the motor to use for calculating the speed percentage

        Returns:
            int: the speed percentage
        """
        return self.percent


class MotorSpeedRPS(MotorSpeed):
    """
    Motor speed in rotations-per-second

    Args:
        rotations_per_second (int): the rotations-per-second to store

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MotorSpeedRPS, SpikeMediumMotor

        # run for 720 degrees at 1.5 rotations-per-second
        mtr = SpikeMediumMotor(hub.port.E)
        mtr.run_for_degrees(720, MotorSpeedRPS(1.5))
    """

    def __init__(self, rotations_per_second):
        self.rotations_per_second = rotations_per_second

    def __str__(self):
        return str(self.rotations_per_second) + " rot/sec"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return MotorSpeedRPS(self.rotations_per_second * other)

    def to_native_units(self, motor):
        """
        Return the speed percentage required to achieve the desired rotations-per-second

        Args:
            motor (Motor): the motor to use for calculating the speed percentage

        Returns:
            int: the speed percentage required to achieve the desired rotations-per-second
        """
        if abs(self.rotations_per_second) > motor.MAX_RPS:
            raise ValueError(
                "invalid rotations-per-second: {} max RPS is {}, {} was requested".format(
                    motor, motor.MAX_RPS, self.rotations_per_second
                )
            )
        return int((self.rotations_per_second / motor.MAX_RPS) * 100)


class MotorSpeedRPM(MotorSpeed):
    """
    Motor speed in rotations-per-minute

    Args:
        rotations_per_minute (int): the rotations-per-minute to store

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MotorSpeedRPM, SpikeMediumMotor

        # run for 720 degrees at 20 rotations-per-minute
        mtr = SpikeMediumMotor(hub.port.E)
        mtr.run_for_degrees(720, MotorSpeedRPM(20))
    """

    def __init__(self, rotations_per_minute):
        self.rotations_per_minute = rotations_per_minute

    def __str__(self):
        return str(self.rotations_per_minute) + " rot/min"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return MotorSpeedRPM(self.rotations_per_minute * other)

    def to_native_units(self, motor):
        """
        Return the speed percentage required to achieve the desired rotations-per-minute

        Args:
            motor (Motor): the motor to use for calculating the speed percentage

        Returns:
            int: the speed percentage required to achieve the desired rotations-per-minute
        """
        if abs(self.rotations_per_minute) > motor.MAX_RPM:
            raise ValueError(
                "invalid rotations-per-minute: {} max RPM is {}, {} was requested".format(
                    motor, motor.MAX_RPM, self.rotations_per_minute
                )
            )
        return int((self.rotations_per_minute / motor.MAX_RPM) * 100)


class MotorSpeedDPS(MotorSpeed):
    """
    Motor speed in degrees-per-second

    Args:
        degrees_per_second (int): the degrees-per-second to store

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MotorSpeedDPS, SpikeMediumMotor

        # run for 720 degrees at 180 degrees-per-second
        mtr = SpikeMediumMotor(hub.port.E)
        mtr.run_for_degrees(720, MotorSpeedDPS(180))
    """

    def __init__(self, degrees_per_second):
        self.degrees_per_second = degrees_per_second

    def __str__(self):
        return str(self.degrees_per_second) + " deg/sec"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return MotorSpeedDPS(self.degrees_per_second * other)

    def to_native_units(self, motor):
        """
        Return the speed percentage required to achieve the desired degrees-per-second

        Args:
            motor (Motor): the motor to use for calculating the speed percentage

        Returns:
            int: the speed percentage required to achieve the desired degrees-per-second
        """
        if abs(self.degrees_per_second) > motor.MAX_DPS:
            raise ValueError(
                "invalid degrees-per-second: {} max DPS is {}, {} was requested".format(
                    motor, motor.MAX_DPS, self.degrees_per_second
                )
            )
        return int((self.degrees_per_second / motor.MAX_DPS) * 100)


class MotorSpeedDPM(MotorSpeed):
    """
    Motor speed in degrees-per-minute

    Args:
        degrees_per_minute (int): the degrees-per-minute to store

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MotorSpeedDPM, SpikeMediumMotor

        # run for 720 degrees at 10000 degrees-per-minute
        mtr = SpikeMediumMotor(hub.port.E)
        mtr.run_for_degrees(720, MotorSpeedDPM(10000))
    """

    def __init__(self, degrees_per_minute):
        self.degrees_per_minute = degrees_per_minute

    def __str__(self):
        return str(self.degrees_per_minute) + " deg/min"

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("{} can only be multiplied by an int or float".format(self))
        return MotorSpeedDPM(self.degrees_per_minute * other)

    def to_native_units(self, motor):
        """
        Return the speed percentage required to achieve the desired degrees-per-minute

        Args:
            motor (Motor): the motor to use for calculating the speed percentage

        Returns:
            int: the speed percentage required to achieve the desired degrees-per-minute
        """
        if abs(self.degrees_per_minute) > motor.MAX_DPM:
            "invalid degrees-per-minute: {} max DPM is {}, {} was requested".format(
                motor, motor.MAX_DPM, self.degrees_per_minute
            )
        return int(self.degrees_per_minute / motor.MAX_DPM * motor.max_speed)


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
    # Derived from:
    #    for x in hub.port.E.info()["modes"]:
    #        print(x)
    POWER = 0
    SPEED = 1
    POS = 2
    APOS = 3  # position but limited to -180 -> 180
    LOAD = 4
    CALIB = 5


class InvalidMotorMode(ValueError):
    pass


# callback() infrastructure
_portletter2motor = {}


def _callback(mtr, reason):
    if reason == MotorCallbackEvent.COMPLETED:
        mtr.interrupted = False
        mtr.stalled = False
        # log_msg("{}: _callback COMPLETED".format(mtr))

    elif reason == MotorCallbackEvent.INTERRUPTED:
        mtr.interrupted = True
        mtr.stalled = False
        log_msg("{}: _callback INTERRUPTED".format(mtr))

    elif reason == MotorCallbackEvent.STALL:
        mtr.interrupted = False
        mtr.stalled = True
        log_msg("{}: _callback STALL".format(mtr))

    else:
        raise ValueError("invalid callback reason {}".format(reason))

    mtr.rxed_callback = True


def _callback_A(reason):
    mtr = _portletter2motor["A"]
    _callback(mtr, reason)


def _callback_B(reason):
    mtr = _portletter2motor["B"]
    _callback(mtr, reason)


def _callback_C(reason):
    mtr = _portletter2motor["C"]
    _callback(mtr, reason)


def _callback_D(reason):
    mtr = _portletter2motor["D"]
    _callback(mtr, reason)


def _callback_E(reason):
    mtr = _portletter2motor["E"]
    _callback(mtr, reason)


def _callback_F(reason):
    mtr = _portletter2motor["F"]
    _callback(mtr, reason)


class Motor:
    """
    A base class for SPIKE motors

    Args:
        port (str): must be A, B, C, D, E or F
        polarity (MotorPolarity): defaults to :class:`MotorPolarity.NORMAL`
        desc (str): defaults to None
    """

    def __init__(self, port, polarity=MotorPolarity.NORMAL, desc=None):
        super().__init__()
        self.port = port
        self.port_letter = str(port)[-2]
        self.interrupted = False
        self.stalled = False
        self.polarity = polarity
        self.desc = desc
        self.rxed_callback = False

        # wait for motor to connect
        while self.port.motor is None:
            utime.sleep(0.1)

        # dwalton
        self.port.motor.mode(MotorMode.POS)

        # callback setup
        if self.port_letter == "A":
            self.port.motor.callback(_callback_A)
        elif self.port_letter == "B":
            self.port.motor.callback(_callback_B)
        elif self.port_letter == "C":
            self.port.motor.callback(_callback_C)
        elif self.port_letter == "D":
            self.port.motor.callback(_callback_D)
        elif self.port_letter == "E":
            self.port.motor.callback(_callback_E)
        elif self.port_letter == "F":
            self.port.motor.callback(_callback_F)
        else:
            raise ValueError("invalid port {}".format(self.port_letter))

        global _portletter2motor
        _portletter2motor[self.port_letter] = self

    def __str__(self):
        if self.desc is not None:
            return self.desc
        else:
            return "{}(port {})".format(self.__class__.__name__, self.port_letter)

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

    def _speed_percentage(self, speed):

        if isinstance(speed, MotorSpeed):
            return speed.to_native_units(self)

        # If speed is not a MotorSpeed object we treat it as a percentage
        elif isinstance(speed, (float, int)):
            return MotorSpeedPercent(speed).to_native_units(self)

        else:
            raise TypeError(type(speed))

    @property
    def position(self):
        """
        Returns:
            int: the motor's position encoder value
        """
        return self.port.motor.get()[0]

    @position.setter
    def position(self, value):
        """
        Set the motor encoder position to ``value``

        Args:
            value (int): the new value for the motor's position encoder
        """
        self.port.motor.preset(value)

    @property
    def is_stalled(self):
        """
        Returns:
            bool: True if the motor has stalled
        """
        return self.stalled

    @property
    def is_running(self):
        """
        Returns:
            bool: True if the motor is running
        """
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

    def init_position(self):
        """
        Initialize the POS value from the APOS value
        """
        self.port.motor.mode(MotorMode.APOS)
        a_pos = self.position
        self.port.motor.mode(MotorMode.POS)
        self.position = a_pos

    def stop(self, stop_action=MotorStop.BRAKE):
        """
        stops the motor

        Args:
            stop_action (MotorStop): defaults to :class:`MotorStop.BRAKE`
        """

        if stop_action == MotorStop.FLOAT:
            self.port.motor.float()

        elif stop_action == MotorStop.BRAKE:
            self.port.motor.brake()

        elif stop_action == MotorStop.HOLD:
            self.port.motor.hold()

        else:
            raise ValueError("invalid stop_action {}".format(stop_action))

    def run_at_speed(self, speed, **kwargs):
        """
        Run the motor at ``speed``. The motor will run until you call ``stop()``

        Args:
            speed (MotorSpeed): the speed of the motor
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """
        raw_speed = self._speed_percentage(speed)
        raw_speed = self._speed_with_polarity(raw_speed)
        self.port.motor.run_at_speed(raw_speed, **kwargs)

    def run_for_degrees(self, degrees, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Run the motor at ``speed`` for ``degrees``

        Args:
            degrees (int): the number of degrees to move the motor
            speed (MotorSpeed): the speed of the motor
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """
        if degrees < 0:
            raise ValueError("degrees was {}, must be >= 0".format(degrees))
        elif degrees == 0:
            return

        raw_speed = self._speed_percentage(speed)
        raw_speed = self._speed_with_polarity(raw_speed)

        # log_msg(
        #     "{}: run_for_degrees {} at speed {}, raw_speed {}, stop {}, block {}".format(
        #         self, degrees, speed, raw_speed, stop, block
        #     )
        # )
        self.rxed_callback = False
        self.port.motor.run_for_degrees(degrees, raw_speed, stop=stop, **kwargs)

        if block:
            self._wait()

    def run_to_position(self, position, speed, direction="shortest", stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Run the motor at ``speed`` to the desired position

        Args:
            position (int): the target position for the left motor
            speed (MotorSpeed): the speed of the motor
            direction (str): one of `clockwise`, `counterclockwise` or `shortest`
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """
        if self.port.motor.mode() != [(2, 0)]:
            raise InvalidMotorMode("MotorMode must be POS, it is {}".format(self.port.motor.mode()))

        delta = abs(self.position - position)

        # If we are already at the target position there is no work to do
        if not delta:
            return

        raw_speed = self._speed_percentage(speed)

        if direction == "clockwise":
            raw_speed = abs(raw_speed)
            raw_speed = self._speed_with_polarity(raw_speed)
        elif direction == "counterclockwise":
            raw_speed = abs(raw_speed) * -1
            raw_speed = self._speed_with_polarity(raw_speed)
        elif direction == "shortest":
            raw_speed = abs(raw_speed)
        else:
            raise ValueError(direction)

        # log_msg(
        #     "{}: run_to_position {} from {} to {} at speed {}, raw_speed {}, stop {}, block {}".format(
        #         self, direction, self.position, position, speed, raw_speed, stop, block
        #     )
        # )
        self.rxed_callback = False

        if direction == "clockwise" or direction == "counterclockwise":
            self.port.motor.run_for_degrees(delta, speed=raw_speed, stop=stop, **kwargs)
        elif direction == "shortest":
            self.port.motor.run_to_position(position, speed=raw_speed, stop=stop, **kwargs)

        if block:
            self._wait()

    def run_for_time(self, msec, speed, stop=MotorStop.BRAKE, block=True, **kwargs):
        """
        Run the motor at ``speed`` for ``msec``

        Args:
            msec (int): the number of milliseconds to run the motor
            speed (MotorSpeed): the speed of the motor
            stop (MotorStop): how to stop the motors, defaults to :class:`MotorStop.BRAKE`
            block (bool): if True this function will not return until the motors have finished moving
            **kwargs: optional kwargs that will pass all the way down to the LEGO ``hub.port.X.motor`` API call
        """

        if msec < 0:
            raise ValueError("msec was {}, must be >= 0".format(msec))
        elif msec == 0:
            return

        raw_speed = self._speed_percentage(speed)
        log_msg(
            "{}: run_for_time {}ms at speed {}, raw_speed {}, stop {}, block {}".format(
                self, msec, speed, raw_speed, stop, block
            )
        )
        self.rxed_callback = False
        self.port_motor.run_for_time(msec, raw_speed, stop=stop, **kwargs)

        if block:
            self._wait()


class SpikeMediumMotor(Motor):
    """
    * part number `54696 <https://brickset.com/parts/design-54696>`_
    * comes in set `45678-1 <https://brickset.com/sets/45678-1/>`_

    .. image:: images/spike-medium-motor.jpg

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MotorSpeedPercent, SpikeMediumMotor

        # run for 720 degrees at 40% of motor's maximum speed
        mtr = SpikeMediumMotor(hub.port.E)
        mtr.run_for_degrees(720, MotorSpeedPercent(40))
    """

    MAX_RPM = 135  # rotations per minute
    MAX_RPS = 2.25  # rotations per second
    MAX_DPM = 48600  # degrees per minute
    MAX_DPS = 810  # degrees per second


class SpikeLargeMotor(Motor):
    """
    * part number `54675 <https://brickset.com/parts/design-54675>`_
    * comes in set `45678-1 <https://brickset.com/sets/45678-1/>`_

    .. image:: images/spike-large-motor.jpg

    Example:

    .. code:: python

        import hub
        from spikedev.motor import MotorSpeedPercent, SpikeLargeMotor

        # run for 720 degrees at 40% of motor's maximum speed
        mtr = SpikeLargeMotor(hub.port.E)
        mtr.run_for_degrees(720, MotorSpeedPercent(40))
    """

    MAX_RPM = 175
    MAX_RPS = 2.916666
    MAX_DPM = 63000
    MAX_DPS = 1050
