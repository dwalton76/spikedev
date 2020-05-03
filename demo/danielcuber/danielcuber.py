"""
DanielCuber
- Daniel Walton
- dwalton76@gmail.com

PORT A - poker motor
PORT C - turntable motor
PORT E - empty

PORT B - color sensor
PORT D - holder/colorsensor motor
"""

# standard libraries
import gc
import utime

# third party libraries
import hub
from rubikscolorresolver import RubiksColorSolverGeneric
from rubikscubesolvermicropython.cube import RubiksCube333

# spikedev libraries
import ujson
from spikedev.logging import log_msg
from spikedev.motor import SpikeLargeMotor, SpikeMediumMotor
from spikedev.sensor import ColorSensor, ColorSensorMode


class DanielCuber(object):
    """
    SPIKE 3x3x3 Rubiks Cube solver
    """

    COLOR_DEGREES_CENTER = -207
    COLOR_DEGREES_HOLD = -195
    COLOR_DEGREES_FLIP = -200
    COLOR_DEGREES_EDGE = -90
    COLOR_DEGREES_CORNER = -70
    COLOR_DEGREES_HOME = 0
    COLOR_SPEED_INIT = 5
    COLOR_SPEED_SCAN = 60
    COLOR_SPEED_FLIP = 75

    POKER_DEGREES_HOME = -12
    POKER_DEGREES_FLIP = 140
    POKER_DEGREES_HOLD = 14
    POKER_SPEED_INIT = 10
    POKER_SPEED_PUSH = 30
    POKER_SPEED_PULL = 40

    # The gear ratio is 28:20 or 1.4
    TURNTABLE_RATIO = 1.4
    TURNTABLE_SPEED = 25
    TURNTABLE_DEGREES_OVERROTATE = 23

    TRANSFORM_ROTATE_CLOCKWISE = (0, 1, 5, 2, 3, 4)
    TRANSFORM_ROTATE_COUNTER_CLOCKWISE = (0, 1, 3, 4, 5, 2)
    TRANSFORM_FLIP = (2, 4, 1, 3, 0, 5)

    def __init__(self):
        self.state = ["U", "D", "F", "L", "B", "R"]  # track which sides are where
        self.shutdown = False
        self.rgb_values = {}
        self.cube_kociemba = None

        # It can take a sec for the motors to connect
        for port in (hub.port.C, hub.port.D, hub.port.F):
            while port.motor is None:
                utime.sleep(0.1)

        self.poker = SpikeMediumMotor(hub.port.D, desc="poker(D)")
        self.turntable = SpikeLargeMotor(hub.port.F, desc="turntable(F)")
        self.colorarm = SpikeMediumMotor(hub.port.C, desc="colorarm(C)")
        self.colorsensor = ColorSensor(hub.port.E, mode=ColorSensorMode.RGB_I)

    def init_motors(self):
        """
        - move poker all the way back
        - move colorarm all the way back
        """
        self.poker.init_position()
        self.turntable.position = 0
        self.colorarm.init_position()

        self.poker.run_to_position(self.POKER_DEGREES_HOME, speed=self.POKER_SPEED_INIT)
        self.colorarm.run_to_position(0, speed=self.COLOR_SPEED_INIT)

    def stop_motors(self):
        self.poker.stop()
        self.turntable.stop()
        self.colorarm.stop()

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

    def colorarm_hold_cube(self):
        """
        Move the color sensor over the middle square, this in turn holds the
        top two layers of the cube.
        """
        self.colorarm.run_to_position(self.COLOR_DEGREES_HOLD, self.COLOR_SPEED_SCAN)

    def colorarm_middle(self):
        """
        Move the color sensor over the middle square, this in turn holds the
        top two layers of the cube.
        """
        self.colorarm.run_to_position(self.COLOR_DEGREES_CENTER, self.COLOR_SPEED_SCAN)

    def colorarm_edge(self, target):
        """
        Move the color sensor over the edge square
        """
        self.colorarm.run_to_position(target, self.COLOR_SPEED_SCAN)

    def colorarm_corner(self, target):
        """
        Move the color sensor over the corner square
        """
        self.colorarm.run_to_position(target, self.COLOR_SPEED_SCAN)

    def colorarm_home(self):
        """
        Move the colorarm all the way out of the way
        """
        self.colorarm.run_to_position(self.COLOR_DEGREES_HOME, self.COLOR_SPEED_SCAN)

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
            self.colorarm_hold_cube()
            self.poker_hold_cube()

        degrees = int(self.TURNTABLE_RATIO * 90 * quarter_turn_count)

        # log_msg("rotate_cube() clockwise %s, quarter_turn_count %s, degrees %d" %
        #    (clockwise, quarter_turn_count, degrees))

        speed = self.TURNTABLE_SPEED

        # When the larger motor is rotating clockwise the turntable will
        # be moving counter-clockwise (because we have an even number of gears).
        # So if we want the turntable to move clockwise, reverse the direction
        # of the large motor.
        if clockwise:
            speed *= -1

        # If hold_cube is True, over-rotate a little then reverse by the over-rotate amount
        if hold_cube:
            self.turntable.run_for_degrees(degrees + self.TURNTABLE_DEGREES_OVERROTATE, speed)
            self.turntable.run_for_degrees(self.TURNTABLE_DEGREES_OVERROTATE, speed * -1)

        else:
            self.turntable.run_for_degrees(degrees, speed)

        if hold_cube:
            self.colorarm_home()
            self.poker_home()

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

    def poker_home(self):
        self.poker.run_to_position(self.POKER_DEGREES_HOME, speed=self.POKER_SPEED_PULL)

    def poker_flip(self):
        self.poker.run_to_position(self.POKER_DEGREES_FLIP, speed=self.POKER_SPEED_PUSH)

    def poker_hold_cube(self):
        self.poker.run_to_position(self.POKER_DEGREES_HOLD, speed=self.POKER_SPEED_PUSH)

    def flip(self, move_colorarm_to_home=True):
        """
        - push the poker arm right next to the cube
        - extend the poker arm quickly to flip the cube over
        - use the colorarm to push the cube back into the middle of the turntable
        """

        if self.shutdown:
            return

        log_msg("flip()")
        self.poker_flip()
        self.poker_home()

        # Move colorarm forward to nudge cube back to the center
        self.colorarm.run_to_position(self.COLOR_DEGREES_FLIP, self.COLOR_SPEED_FLIP)

        if move_colorarm_to_home:
            self.colorarm.run_to_position(self.COLOR_DEGREES_HOME, self.COLOR_SPEED_FLIP)

        self.apply_transformation(self.TRANSFORM_FLIP)

    def _rotate_one_eighth(self):
        """
        Rotate the turntable counter-clockwise for 1/8th of a turn. This is
        used when scanning the cube colors.
        """
        # (360 / 8) * TURNTABLE_RATIO = 63
        self.turntable.run_for_degrees(63, self.TURNTABLE_SPEED)

    def rotate_from_corner_to_edge(self):
        self._rotate_one_eighth()

    def rotate_from_edge_to_corner(self):
        self._rotate_one_eighth()

    def scan_side(self, side_name, scan_order):
        """
        Scan all 9 squares of a cube side, return a list of the side name for each square
        """
        log_msg("scan_side() {} in scan_order {}".format(side_name, scan_order))

        # This needs more tweaking, we are getting dark/inconsistent readings out of the color sensor
        # due to how it is positioned over the various squares
        target = [
            self.COLOR_DEGREES_CENTER,
            -120,  # 1st edge
            -90,  # 1st corner
            -110,  # 2nd edge
            -80,  # 2nd corner
            -115,  # 3rd edge
            -95,  # 3rd corner
            -105,  # 4th edge
            -75,  # 4th corner
        ]

        # scan all four corners and edges
        for x in range(9):
            square_index = scan_order[x]

            # scan the middle
            if x == 0:
                self.colorarm_middle()
                self.rgb_values[square_index] = self.colorsensor.rgb()

            # scan an edge
            elif x % 2 == 1:

                # 1st edge - we just scanned the middle square
                if x == 1:
                    self.colorarm_edge(target[x])
                    self.rgb_values[square_index] = self.colorsensor.rgb()

                # 2nd/3rd/4th edge - we just scanned a corner square
                else:
                    self.colorarm_home()
                    self.rotate_from_corner_to_edge()
                    self.colorarm_edge(target[x])
                    self.rgb_values[square_index] = self.colorsensor.rgb()

            # scan a corner
            else:
                self.colorarm_home()
                self.rotate_from_edge_to_corner()
                self.colorarm_corner(target[x])
                self.rgb_values[square_index] = self.colorsensor.rgb()

        # rotate back to original edge
        self.colorarm_home()
        self.rotate_from_corner_to_edge()

    def scan(self):
        """
        scan the entire cube
        """
        log_msg("scan()")
        self.rgb_values = {}

        # U
        self.scan_side("U", (5, 6, 9, 8, 7, 4, 1, 2, 3))

        # L
        self.flip(move_colorarm_to_home=False)
        self.scan_side("L", (14, 11, 12, 15, 18, 17, 16, 13, 10))

        # D
        self.flip(move_colorarm_to_home=False)
        self.scan_side("D", (50, 49, 46, 47, 48, 51, 54, 53, 52))

        # R
        self.flip(move_colorarm_to_home=False)
        self.scan_side("R", (32, 35, 34, 31, 28, 29, 30, 33, 36))

        # F
        self.rotate_cube(clockwise=True, quarter_turn_count=1, hold_cube=False)
        self.flip(move_colorarm_to_home=False)
        self.scan_side("F", (23, 24, 27, 26, 25, 22, 19, 20, 21))

        # B
        self.flip(move_colorarm_to_home=True)
        self.flip(move_colorarm_to_home=False)
        self.scan_side("D", (41, 42, 45, 44, 43, 40, 37, 38, 39))

        # Use the color resolver library to examine the RGB values and extract
        # the state of the cube
        log_msg("RGB json:\n{}\n".format(ujson.dumps(self.rgb_values)))
        rgb_solver = RubiksColorSolverGeneric(3)
        rgb_solver.enter_scan_data(self.rgb_values)
        self.rgb_values = {}
        gc.collect()
        rgb_solver.crunch_colors()
        self.cube_kociemba = rgb_solver.cube_for_kociemba_strict()
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

        log_msg("move_side_to_down() side{}".format(side))

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
        last_step_index = len(SIDE_DOWN_STEPS[position]) - 1

        for (step_index, step) in enumerate(SIDE_DOWN_STEPS[position]):
            if step == "flip":
                if step_index == last_step_index:
                    self.flip(move_colorarm_to_home=False)
                else:
                    self.flip(move_colorarm_to_home=True)
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

            log_msg("Move {}/{}: {}".format(index + 1, total_steps, step))
            side = list(step)[0]
            self.move_side_to_down(side)

            if step.endswith("'"):
                self.rotate_cube_blocked_clockwise_quarter_turn()

            elif step.endswith("2"):
                self.rotate_cube_blocked_clockwise_half_turn()

            else:
                self.rotate_cube_blocked_counter_clockwise_quarter_turn()


if __name__ == "__main__":
    CUBE_ICON = hub.Image("00555:09995:09995:09990:00000")
    hub.display.show(CUBE_ICON)
    hub.led(255, 0, 0)

    # sleep 3s for the hub to init all motor and sensors
    utime.sleep(3)
    spike = DanielCuber()
    spike.init_motors()
    hub.led(0, 0, 255)
    spike.wait_for_button_press()
    hub.led(0, 255, 0)

    # spike.colorarm_middle()
    # spike.colorarm_edge()
    # spike.colorarm_home()
    # spike.flip()
    # spike.rotate_cube_blocked_clockwise_quarter_turn()

    try:
        spike.scan()
        spike.solve()
    except Exception:
        spike.stop_motors()
        raise

    hub.led(255, 255, 255)
    hub.display.show(hub.Image.HEART_SMALL)
    spike.stop_motors()
