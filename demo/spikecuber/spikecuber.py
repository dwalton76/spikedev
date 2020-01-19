"""
SpikeCuber
- Daniel Walton
- dwalton76@gmail.com

PORT A - poker motor
PORT C - turntable motor
PORT E - empty

PORT B - color sensor
PORT D - holder/colorsensor motor
"""

# standard libraries
import utime

# third party libraries
import hub
from rubikscolorresolver.base import RubiksColorSolverGenericBase
from rubikscubesolvermicropython.cube import RubiksCube333
from util.sensors import get_sensor_value

# spikedev libraries
from spikedev.logging import log_msg
from spikedev.motor import SpikeLargeMotor, SpikeMediumMotor

BLACK = 0
VIOLET = 1
BLUE = 3
AZURE = 4
GREEN = 5
YELLOW = 7
RED = 9
WHITE = 10

# The sensor does not officially detect Orange
color_to_side = {WHITE: "U", YELLOW: "D", GREEN: "F", BLUE: "B", RED: "R"}


def color_sensor_to_side_name():
    sensor_value = get_sensor_value("B", 0, -1, (61,))
    return color_to_side.get(sensor_value, "L")


# def print_mem_stats(desc):
#    import gc
#    log_msg('{} free: {} allocated: {}'.format(desc, gc.mem_free(), gc.mem_alloc()))


class SpikeCuber(object):
    """
    SPIKE 3x3x3 Rubiks Cube solver
    """

    COLOR_SENSOR_CENTER_DEGREES = 120
    COLOR_SENSOR_EDGE_DEGREES = 210
    COLOR_SENSOR_CORNER_DEGREES = 235
    COLOR_SENSOR_HOME_DEGREES = 0

    TRANSFORM_ROTATE_CLOCKWISE = (0, 1, 5, 2, 3, 4)
    TRANSFORM_ROTATE_COUNTER_CLOCKWISE = (0, 1, 3, 4, 5, 2)
    TRANSFORM_FLIP = (2, 4, 1, 3, 0, 5)

    # The gear ratio is 7:5 aka 1.4
    TURNTABLE_RATIO = 1.4

    def __init__(self):
        self.state = ["U", "D", "F", "L", "B", "R"]  # track which sides are where
        self.shutdown = False
        self.cube_kociemba = None

        # It can take a sec for the motors to connect
        for port in (hub.port.A, hub.port.C, hub.port.D):
            while port.motor is None:
                utime.sleep(0.1)

        self.poker = SpikeMediumMotor(hub.port.A, desc="poker(A)")
        self.turntable = SpikeLargeMotor(hub.port.C, desc="turntable(C)")
        self.colorarm = SpikeMediumMotor(hub.port.D, desc="colorarm(D)")

    def init_motors(self):
        """
        - move poker all the way back
        - move colorarm all the way back
        """
        self.poker.position = 0
        self.turntable.position = 0
        self.colorarm.position = 0

    def wait_for_button_press(self):
        """
        Wait for the user to press the left or right button to indicate
        they are ready for the cube to be solved
        """
        while not hub.button.left.is_pressed() and not hub.button.right.is_pressed():
            pass

    def apply_transformation(self, transformation):
        """
        Update the cube state based on 'transformation'
        """
        self.state = [self.state[x] for x in transformation]

    def colorarm_guts(self, degrees, speed):
        def get_current_degrees():
            current_degrees = get_sensor_value("D", 3, 0, (49, 48))

            if abs(current_degrees) > 360:
                current_degrees = current_degrees % 360

            return current_degrees

        current_degrees = get_current_degrees()

        if degrees == self.COLOR_SENSOR_CENTER_DEGREES:
            direction = "counterclockwise"

        elif degrees == self.COLOR_SENSOR_HOME_DEGREES:
            direction = "clockwise"

        else:

            if degrees == self.COLOR_SENSOR_EDGE_DEGREES:
                # If we are currently at the middle position move clockwise
                # to get to the edge position
                if abs(self.COLOR_SENSOR_CENTER_DEGREES - current_degrees) <= 20:
                    direction = "clockwise"
                else:
                    direction = "counterclockwise"

            elif degrees == self.COLOR_SENSOR_CORNER_DEGREES:
                # If we are at the home position move counter-clockwise
                # to get to the corner position
                if current_degrees >= 350 or current_degrees <= 10:
                    direction = "counterclockwise"
                else:
                    direction = "clockwise"

        log_msg(
            "colorarm_guts at {}, go {} to degrees {}, speed {}, motor {}".format(
                current_degrees, direction, degrees, speed, self.colorarm
            )
        )

        # Motor go direction to position
        self.colorarm.run_to_position(degrees, speed, direction)

        # Where did we end up
        current_degrees = get_current_degrees()
        log_msg("colorarm_guts at {}\n\n".format(current_degrees))

    def colorarm_middle(self):
        """
        Move the color sensor over the middle square, this in turn holds the
        top two layers of the cube.
        """
        log_msg("colorarm_middle()")
        self.colorarm_guts(degrees=self.COLOR_SENSOR_CENTER_DEGREES, speed=20)

    def colorarm_edge(self):
        """
        Move the color sensor over the edge square
        """
        log_msg("colorarm_edge()")
        self.colorarm_guts(degrees=self.COLOR_SENSOR_EDGE_DEGREES, speed=20)

    def colorarm_corner(self):
        """
        Move the color sensor over the corner square
        """
        log_msg("colorarm_corner()")
        self.colorarm_guts(degrees=self.COLOR_SENSOR_CORNER_DEGREES, speed=20)

    def colorarm_home(self):
        """
        Move the colorarm all the way out of the way
        """
        log_msg("colorarm_home()")
        self.colorarm_guts(degrees=self.COLOR_SENSOR_HOME_DEGREES, speed=20)

    def rotate_cube(self, clockwise, quarter_turn_count, hold_cube):
        """
        Rotate the turntable
        """
        assert isinstance(clockwise, bool)
        assert isinstance(quarter_turn_count, int)
        assert isinstance(hold_cube, bool)
        assert quarter_turn_count in (1, 2)

        if self.shutdown:
            return

        if hold_cube:
            self.colorarm_middle()

        degrees = self.TURNTABLE_RATIO * 90 * quarter_turn_count

        # log_msg("rotate_cube() clockwise %s, quarter_turn_count %s, degrees %d" %
        #    (clockwise, quarter_turn_count, degrees))

        speed = 50

        # When the larger motor is rotating clockwise the turntable will
        # be moving counter-clockwise (because we have an even number of gears).
        # So if we want the turntable to move clockwise, reverse the direction
        # of the large motor.
        if clockwise:
            speed *= -1

        # If hold_cube is True, over-rotate a little then reverse by the over-rotate amount
        if hold_cube:
            OVER_ROTATE_DEGREES = 12
            self.turntable.run_for_degrees(degrees + OVER_ROTATE_DEGREES, speed)
            self.turntable.run_for_degrees(OVER_ROTATE_DEGREES, speed * -1)

        else:
            self.turntable.run_for_degrees(degrees, speed)

        if hold_cube:
            self.colorarm_home()

        else:
            # If we are not holding the top two layers then the entire cube rotated.
            # Update our state that tracks which sides are facing which direction.
            for i in range(quarter_turn_count):
                if clockwise:
                    self.apply_transformation(self.TRANSFORM_ROTATE_CLOCKWISE)
                else:
                    self.apply_transformation(self.TRANSFORM_ROTATE_COUNTER_CLOCKWISE)

    def rotate_cube_clockwise_quarter_turn(self):
        """
        rotate the cube clockwise one quarter turn
        """
        self.rotate_cube(clockwise=True, quarter_turn_count=1, hold_cube=False)

    def rotate_cube_clockwise_half_turn(self):
        """
        rotate the cube clockwise one half turn
        """
        self.rotate_cube(clockwise=True, quarter_turn_count=2, hold_cube=False)

    def rotate_cube_counter_clockwise_quarter_turn(self):
        """
        rotate the cube counter-clockwise one quarter turn
        """
        self.rotate_cube(clockwise=False, quarter_turn_count=1, hold_cube=False)

    def rotate_cube_blocked_clockwise_quarter_turn(self):
        """
        rotate the bottom layer clockwise one quarter turn
        """
        self.rotate_cube(clockwise=True, quarter_turn_count=1, hold_cube=True)

    def rotate_cube_blocked_clockwise_half_turn(self):
        """
        rotate the bottom layer clockwise one half turn
        """
        self.rotate_cube(clockwise=True, quarter_turn_count=2, hold_cube=True)

    def rotate_cube_blocked_counter_clockwise_quarter_turn(self):
        """
        rotate the bottom layer counter-clockwise one quarter turn
        """
        self.rotate_cube(clockwise=False, quarter_turn_count=1, hold_cube=True)

    def flip_guts(self):
        poker_degrees = 140
        push_center_degrees = 120

        self.poker.run_to_position(poker_degrees, 60, "clockwise")
        self.poker.run_to_position(347, 60, "counterclockwise")

        # Move colorarm forward to nudge cube
        self.colorarm.run_to_position(push_center_degrees, 75, "counterclockwise")
        self.colorarm.run_to_position(0, 75, "clockwise")

    def flip(self):
        """
        - push the poker arm right next to the cube
        - extend the poker arm quickly to flip the cube over
        - use the colorarm to push the cube back into the middle of the turntable
        """

        if self.shutdown:
            return

        log_msg("flip()")
        self.flip_guts()

        self.apply_transformation(self.TRANSFORM_FLIP)

    def _rotate_one_eighth(self):
        """
        Rotate the turntable counter-clockwise for 1/8th of a turn. This is
        used when scanning the cube colors.
        """
        speed = 20

        # 360/8 is 45
        degrees = int(45 * self.TURNTABLE_RATIO)

        self.turntable.run_for_degrees(degrees, speed)

    def rotate_from_corner_to_edge(self):
        self._rotate_one_eighth()

    def rotate_from_edge_to_corner(self):
        self._rotate_one_eighth()

    def scan_side(self, side_number):
        """
        Scan all 9 squares of a cube side, return a list of the side name for each square
        """
        side_names = []

        if self.shutdown:
            return side_names

        log_msg("scan_side() %d/6" % side_number)

        # scan the middle
        self.colorarm_middle()
        side_names.append(color_sensor_to_side_name())

        # scan all four corners and edges
        for x in range(4):

            # 1st edge - we just scanned the middle square
            if x == 0:
                self.colorarm_edge()
                side_names.append(color_sensor_to_side_name())

            # 2nd/3rd/4th edge - we just scanned a corner square
            else:
                self.colorarm_home()
                self.rotate_from_corner_to_edge()
                self.colorarm_edge()
                side_names.append(color_sensor_to_side_name())

            # corner
            self.colorarm_home()
            self.rotate_from_edge_to_corner()
            self.colorarm_corner()
            side_names.append(color_sensor_to_side_name())

        # rotate back to original edge
        self.rotate_from_corner_to_edge()

        return side_names

    def scan(self):
        """
        scan the entire cube
        """
        log_msg("scan()")
        SCAN_ORDER = {
            "U": (5, 6, 3, 2, 1, 4, 7, 8, 9),
            "L": (14, 15, 12, 11, 10, 13, 16, 17, 18),
            "F": (23, 24, 21, 20, 19, 22, 25, 26, 27),
            "R": (32, 33, 30, 29, 28, 31, 34, 35, 36),
            "B": (41, 42, 39, 38, 37, 40, 43, 44, 45),
            "D": (50, 51, 48, 47, 46, 49, 52, 53, 54),
        }

        # U
        side_names_U = self.scan_side(1)

        # L
        self.flip()
        self.rotate_cube(clockwise=False, quarter_turn_count=1, hold_cube=False)
        side_names_L = self.scan_side(2)

        # B
        self.flip()
        side_names_B = self.scan_side(6)

        # R
        self.flip()
        side_names_R = self.scan_side(4)

        # F
        self.flip()
        side_names_F = self.scan_side(5)

        # D
        self.rotate_cube(clockwise=True, quarter_turn_count=1, hold_cube=False)
        self.flip()
        self.rotate_cube(clockwise=False, quarter_turn_count=1, hold_cube=False)
        side_names_D = self.scan_side(3)

        # kociemba order is URFDLB
        side_names = []
        side_names.extend(side_names_U)
        side_names.extend(side_names_R)
        side_names.extend(side_names_F)
        side_names.extend(side_names_D)
        side_names.extend(side_names_L)
        side_names.extend(side_names_B)
        kociemba_string = "".join(side_names)
        log_msg("kociemba_string (init) {}".format(kociemba_string))

        # Use the color resolver library to make sure our cube state is valid. If it
        # isn't valid the color resolver will change some colors around to make it valid.
        #
        # Commenting out for now as loading this module runs us out of memory :(
        """
        cube = RubiksColorSolverGenericBase(3)
        cube.enter_cube_state(kociemba_string)
        cube.sanity_check_edge_squares()
        cube.validate_all_corners_found()
        cube.validate_odd_cube_midge_vs_corner_parity()
        self.cube_kociemba = "".join(cube.cube_for_kociemba_strict())
        """
        self.cube_kociemba = kociemba_string
        log_msg("kociemba_string (final) {}".format(self.cube_kociemba))

        # This is only used if you want to rotate the cube so U is on top, F is
        # in the front, etc. You would do this if you were troubleshooting color
        # detection and you want to pause to compare the color pattern on the
        # cube vs. what we think the color pattern is.
        """
        log_msg("Position the cube so that U is on top, F is in the front, etc...to make debugging easier")
        self.flip()
        self.flip()
        self.rotate_cube(clockwise=True, quarter_turn_count=2, hold_cube=False)
        input('Paused')
        """

    def move_side_to_down(self, side):
        """
        Move 'side' so that it is facing down into the turntable
        """

        log_msg("move_side_to_down() side%s" % side)

        # Get the steps need to move 'side' so that it is facing down
        SIDE_DOWN_STEPS = {
            0: ["flip", "flip"],
            1: [],
            2: ["rotate_cube_clockwise_half_turn", "flip"],
            3: ["rotate_cube_clockwise_quarter_turn", "flip"],
            4: ["flip"],
            5: ["rotate_cube_counter_clockwise_quarter_turn", "flip"],
        }
        position = self.state.index(side)

        for step in SIDE_DOWN_STEPS[position]:
            if step == "flip":
                self.flip()
            elif step == "rotate_cube_clockwise_quarter_turn":
                self.rotate_cube_clockwise_quarter_turn()
            elif step == "rotate_cube_clockwise_half_turn":
                self.rotate_cube_clockwise_half_turn()
            elif step == "rotate_cube_counter_clockwise_quarter_turn":
                self.rotate_cube_counter_clockwise_quarter_turn()
            else:
                raise Exception("invalid step '%s'" % step)

    def solve(self):
        """
        This assumes we have scanned the cube and resolved the raw RGB values
        to the cube state.
        """
        assert self.cube_kociemba is not None, "scan() must be called first"

        cube = RubiksCube333(self.cube_kociemba, "URFDLB")
        solution = cube.solve()
        log_msg("SOLUTION: %s" % " ".join(solution))
        total_steps = len(solution)

        for (index, step) in enumerate(solution):

            if self.shutdown:
                break

            log_msg("Move %d/%d: %s" % (index + 1, total_steps, step))
            side = list(step)[0]
            self.move_side_to_down(side)

            if step.endswith("'"):
                self.rotate_cube_blocked_clockwise_quarter_turn()

            elif step.endswith("2"):
                self.rotate_cube_blocked_clockwise_half_turn()

            else:
                self.rotate_cube_blocked_counter_clockwise_quarter_turn()


if __name__ == "__main__":
    spike = SpikeCuber()
    spike.init_motors()

    spike.rotate_from_corner_to_edge()
    # spike.colorarm_middle()
    # spike.colorarm_home()
    # spike.scan_side(1)

    """
    try:

        while True:
            CUBE_ICON = hub.Image("00555:09995:09995:09990:00000")
            hub.display.show(CUBE_ICON)
            # spike.init_motors()

            hub.led(0, 0, 255)
            spike.wait_for_button_press()
            hub.led(0, 255, 0)

            spike.scan()
            spike.solve()

    except Exception as e:
        log_exception(e)
    """

    hub.led(0, 0, 0)
    hub.display.show(hub.Image.HEART_SMALL)
