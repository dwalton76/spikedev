"""
Advanced Driving Base

Build Instructions
- https://le-www-live-s.legocdn.com/sc/media/lessons/prime/pdf/building-instructions/advanced-driving-base-bi-pdf-book1of5-27819f7532ef6f923878bcc6caf216b7.pdf  # noqa: E501
- https://le-www-live-s.legocdn.com/sc/media/lessons/prime/pdf/building-instructions/advanced-driving-base-bi-pdf-book2of5-3c8e4219dc21da57385208c3c6e338c5.pdf  # noqa: E501
- https://le-www-live-s.legocdn.com/sc/media/lessons/prime/pdf/building-instructions/advanced-driving-base-bi-pdf-book3of5-0cf02cc97c424018c2705d6fc6607f61.pdf  # noqa: E501
- https://le-www-live-s.legocdn.com/sc/media/lessons/prime/pdf/building-instructions/advanced-driving-base-bi-pdf-book4of5-7abb2386053e6137e074b6e9e0a5ea78.pdf  # noqa: E501
- https://le-www-live-s.legocdn.com/sc/media/lessons/prime/pdf/building-instructions/advanced-driving-base-bi-pdf-book5of5-feebc5b3d0c8bd90919806102e5152c4.pdf  # noqa: E501
"""

# standard libraries
import math
import utime

# third party libraries
import hub

# spikedev libraries
from spikedev.motor import MotorSpeedPercent, SpikeLargeMotor, SpikeMediumMotor
from spikedev.sensor import ColorSensor
from spikedev.tank import MoveDifferential
from spikedev.unit import DistanceInches, DistanceStuds
from spikedev.wheel import SpikeLargeWheel

utime.sleep(1)
# bulldozer: 0 is raised, -180 is lowered
# lift arm: 0 is vertical/raised, -180 is horizontal/lowered

adb = MoveDifferential(hub.port.A, hub.port.E, SpikeLargeWheel, DistanceStuds(19), motor_class=SpikeLargeMotor)
adb.rear_motor = SpikeMediumMotor(hub.port.C)
adb.front_motor = SpikeMediumMotor(hub.port.D)
adb.left_color_sensor = ColorSensor(hub.port.B)
adb.right_color_sensor = ColorSensor(hub.port.F)

adb.turn_right(90, MotorSpeedPercent(20))
adb.run_for_distance(DistanceInches(12), MotorSpeedPercent(50))

# drive halfway around a cirle with a radius of 8 inches
adb.run_arc_right(DistanceInches(8), DistanceInches(8) * math.pi, MotorSpeedPercent(20))

# adb.turn_left(90, MotorSpeedPercent(20))
