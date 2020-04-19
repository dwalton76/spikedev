# third party libraries
import hub
from util.scratch import clamp, compare, convert_image, number_color_to_rgb, sanitize_ports, to_number
from util.sensors import get_sensor_value

# spikedev libraries
from runtime import MultiTask, VirtualMachine
from uasyncio.core import sleep_ms


# Procedures definition
async def proc(vm, stack):
    # Data setvariableto
    vm.vars["CUBE_ICON"] = "0055509995099950999000000"
    # Led image
    vm.system.display.show(
        hub.Image(convert_image(vm.vars["CUBE_ICON"], vm.store.get("display_brightness", 100))), clear=False
    )


# Procedures definition
async def proc_1(vm, stack):
    # Data setvariableto
    position = get_sensor_value(vm.vars["PORT_TURNTABLE"], 3, 0, (49, 48))
    if position < 0:
        position = position + 360
    vm.vars["motor_position"] = position
    # Motor turn for counterclockwise
    multitask = MultiTask(vm)
    for port in sanitize_ports(vm.vars["PORT_TURNTABLE"]):
        multitask.store_task(
            "motor_laststatus_" + port,
            vm.system.motors.on_port(port).run_for_degrees,
            round(clamp(45 * to_number(vm.vars["TURNTABLE_RATIO"]), -4294967296, 4294967295)),
            -vm.store.get("motor_speed_" + port, 75),
            stall=vm.store.get("motor_stall_" + port, True),
        )
    await multitask.await_all()


# Procedures definition
async def proc_2(vm, stack):
    # Procedures call
    await proc_9(vm, stack, vm.vars["COLORARM_MIDDLE"], vm.vars["SPEED_COLORARM"])


# Procedures definition
async def proc_3(vm, stack):
    # Procedures call
    await proc_9(vm, stack, vm.vars["COLORARM_CORNER"], vm.vars["SPEED_COLORARM"])


# Procedures definition
async def proc_4(vm, stack):
    # Data setvariableto
    sensor_value = get_sensor_value(vm.vars["PORT_COLORSENSOR"], 0, -1, (61,))
    if sensor_value is None:
        sensor_value = -1
    vm.vars["current_color"] = sensor_value
    # Data addtolist
    vm.lists["colors"].append(vm.vars["current_color"])
    # Procedures call
    await proc_15(vm, stack, vm.vars["current_color"])


# Procedures definition
async def proc_5(vm, stack):
    # Procedures call
    await proc_6(vm, stack, "U")
    # Procedures call
    await proc_10(vm, stack)
    # Procedures call
    await proc_11(vm, stack, "False", "1", "False")
    # Procedures call
    await proc_6(vm, stack, "L")
    # Procedures call
    await proc_10(vm, stack)
    # Procedures call
    await proc_6(vm, stack, "B")
    # Procedures call
    await proc_10(vm, stack)
    # Procedures call
    await proc_6(vm, stack, "R")
    # Procedures call
    await proc_10(vm, stack)
    # Procedures call
    await proc_6(vm, stack, "F")
    # Procedures call
    await proc_11(vm, stack, "True", "1", "False")
    # Procedures call
    await proc_10(vm, stack)
    # Procedures call
    await proc_11(vm, stack, "False", "1", "False")
    # Procedures call
    await proc_6(vm, stack, "D")


# Procedures definition
async def proc_6(vm, stack, proc_6_side_name):
    # Led text
    await vm.system.display.write_async(proc_6_side_name)
    # Control wait
    await sleep_ms(500)
    # Data deletealloflist
    vm.lists["colors"].clear()
    # Data setvariableto
    vm.vars["x"] = "1"
    # Procedures call
    await proc_2(vm, stack)
    # Led image
    index = int(to_number(vm.vars["x"])) - 1
    if 0 <= index < len(vm.lists["scan_displays"]):
        item = vm.lists["scan_displays"][index]
    else:
        item = ""
    vm.system.display.show(hub.Image(convert_image(item, vm.store.get("display_brightness", 100))), clear=False)
    # Procedures call
    await proc_4(vm, stack)
    # Control repeat
    for _ in range(4):
        # Data changevariableby
        vm.vars["x"] = str(to_number(vm.vars["x"]) + 1)
        # Control if else
        if compare(vm.vars["x"], "2") == 0:
            # Procedures call
            await proc_8(vm, stack)
            # Led image
            index_1 = int(to_number(vm.vars["x"])) - 1
            if 0 <= index_1 < len(vm.lists["scan_displays"]):
                item_1 = vm.lists["scan_displays"][index_1]
            else:
                item_1 = ""
            vm.system.display.show(
                hub.Image(convert_image(item_1, vm.store.get("display_brightness", 100))), clear=False
            )
            # Procedures call
            await proc_4(vm, stack)
        else:
            # Procedures call
            await proc_7(vm, stack)
            # Procedures call
            await proc_1(vm, stack)
            # Procedures call
            await proc_8(vm, stack)
            # Led image
            index_2 = int(to_number(vm.vars["x"])) - 1
            if 0 <= index_2 < len(vm.lists["scan_displays"]):
                item_2 = vm.lists["scan_displays"][index_2]
            else:
                item_2 = ""
            vm.system.display.show(
                hub.Image(convert_image(item_2, vm.store.get("display_brightness", 100))), clear=False
            )
            # Procedures call
            await proc_4(vm, stack)
        # Procedures call
        await proc_7(vm, stack)
        # Procedures call
        await proc_1(vm, stack)
        # Procedures call
        await proc_3(vm, stack)
        # Procedures call
        await proc_4(vm, stack)
        # Data changevariableby
        vm.vars["x"] = str(to_number(vm.vars["x"]) + 1)
        # Led image
        index_3 = int(to_number(vm.vars["x"])) - 1
        if 0 <= index_3 < len(vm.lists["scan_displays"]):
            item_3 = vm.lists["scan_displays"][index_3]
        else:
            item_3 = ""
        vm.system.display.show(hub.Image(convert_image(item_3, vm.store.get("display_brightness", 100))), clear=False)
        yield
    # Procedures call
    await proc_7(vm, stack)
    # Procedures call
    await proc_1(vm, stack)
    # Procedures call
    if all([isinstance(x, str) and (len(x) == 1) for x in vm.lists["colors"]]):
        contents = "".join(vm.lists["colors"])
    else:
        contents = " ".join([str(i) for i in vm.lists["colors"]])
    await proc_14(vm, stack, contents)


# When program starts
async def stack_1(vm, stack):
    # Procedures call
    await proc_13(vm, stack)
    # Procedures call
    await proc(vm, stack)
    # Procedures call
    await proc_12(vm, stack)
    # Procedures call
    await proc_5(vm, stack)


# Procedures definition
async def proc_7(vm, stack):
    # Procedures call
    await proc_9(vm, stack, vm.vars["COLORARM_HOME"], vm.vars["SPEED_COLORARM"])
    # Motor stop
    for port_1 in sanitize_ports(vm.vars["PORT_COLORARM"]):
        vm.system.motors.on_port(port_1).hold()


# Procedures definition
async def proc_8(vm, stack):
    # Procedures call
    await proc_9(vm, stack, vm.vars["COLORARM_EDGE"], vm.vars["SPEED_COLORARM"])


# Procedures definition
async def proc_9(vm, stack, proc_9_degrees, proc_9_speed):
    # Data setvariableto
    position_1 = get_sensor_value(vm.vars["PORT_COLORARM"], 3, 0, (49, 48))
    if position_1 < 0:
        position_1 = position_1 + 360
    vm.vars["motor_position"] = position_1
    # Control if
    if compare(proc_9_degrees, vm.vars["COLORARM_MIDDLE"]) == 0:
        # Data setvariableto
        vm.vars["direction"] = "counterclockwise"
    # Control if
    if compare(proc_9_degrees, vm.vars["COLORARM_HOME"]) == 0:
        # Data setvariableto
        vm.vars["direction"] = "clockwise"
    # Control if
    if compare(proc_9_degrees, vm.vars["COLORARM_EDGE"]) == 0:
        # Control if else
        if compare(abs(to_number(vm.vars["COLORARM_MIDDLE"]) - to_number(vm.vars["motor_position"])), "20") < 0:
            # Data setvariableto
            vm.vars["direction"] = "clockwise"
        else:
            # Data setvariableto
            vm.vars["direction"] = "counterclockwise"
    # Control if
    if compare(proc_9_degrees, vm.vars["COLORARM_CORNER"]) == 0:
        # Control if else
        if (compare(vm.vars["motor_position"], "340") > 0) or (compare(vm.vars["motor_position"], "20") < 0):
            # Data setvariableto
            vm.vars["direction"] = "counterclockwise"
        else:
            # Data setvariableto
            vm.vars["direction"] = "clockwise"
    # Control if else
    if compare(vm.vars["direction"], "clockwise") == 0:
        # Motor go direction to position
        multitask_1 = MultiTask(vm)
        for port_2 in sanitize_ports(vm.vars["PORT_COLORARM"]):
            multitask_1.store_task(
                "motor_laststatus_" + port_2,
                vm.system.motors.on_port(port_2).run_go_direction_to_position,
                clamp(to_number(proc_9_degrees), -4294967296, 4294967295),
                abs(vm.store.get("motor_speed_" + port_2, 75)),
                "clockwise",
                stall=vm.store.get("motor_stall_" + port_2, True),
            )
        await multitask_1.await_all()
    else:
        # Motor go direction to position
        multitask_2 = MultiTask(vm)
        for port_3 in sanitize_ports(vm.vars["PORT_COLORARM"]):
            multitask_2.store_task(
                "motor_laststatus_" + port_3,
                vm.system.motors.on_port(port_3).run_go_direction_to_position,
                clamp(to_number(proc_9_degrees), -4294967296, 4294967295),
                abs(vm.store.get("motor_speed_" + port_3, 75)),
                "counterclockwise",
                stall=vm.store.get("motor_stall_" + port_3, True),
            )
        await multitask_2.await_all()


# Procedures definition
async def proc_10(vm, stack):
    # Motor go direction to position
    multitask_3 = MultiTask(vm)
    for port_4 in sanitize_ports(vm.vars["PORT_FLIPPER"]):
        multitask_3.store_task(
            "motor_laststatus_" + port_4,
            vm.system.motors.on_port(port_4).run_go_direction_to_position,
            140,
            abs(vm.store.get("motor_speed_" + port_4, 75)),
            "clockwise",
            stall=vm.store.get("motor_stall_" + port_4, True),
        )
    await multitask_3.await_all()
    # Motor go direction to position
    multitask_4 = MultiTask(vm)
    for port_5 in sanitize_ports(vm.vars["PORT_FLIPPER"]):
        multitask_4.store_task(
            "motor_laststatus_" + port_5,
            vm.system.motors.on_port(port_5).run_go_direction_to_position,
            345,
            abs(vm.store.get("motor_speed_" + port_5, 75)),
            "counterclockwise",
            stall=vm.store.get("motor_stall_" + port_5, True),
        )
    await multitask_4.await_all()
    # Motor stop
    for port_6 in sanitize_ports(vm.vars["PORT_FLIPPER"]):
        vm.system.motors.on_port(port_6).hold()
    # Procedures call
    await proc_2(vm, stack)
    # Procedures call
    await proc_7(vm, stack)


# Procedures definition
async def proc_11(vm, stack, proc_11_clockwise, proc_11_quarter_turn_count, proc_11_hold_cube):
    # Data setvariableto
    vm.vars["OVER_ROTATE"] = "12"
    # Control if else
    if compare(proc_11_hold_cube, "True") == 0:
        # Procedures call
        await proc_2(vm, stack)
        # Control if else
        if compare(proc_11_clockwise, "True") == 0:
            # Motor turn for counterclockwise
            multitask_5 = MultiTask(vm)
            for port_7 in sanitize_ports(vm.vars["PORT_TURNTABLE"]):
                multitask_5.store_task(
                    "motor_laststatus_" + port_7,
                    vm.system.motors.on_port(port_7).run_for_degrees,
                    round(
                        clamp(
                            (to_number(proc_11_quarter_turn_count) * (90 * to_number(vm.vars["TURNTABLE_RATIO"])))
                            + to_number(vm.vars["OVER_ROTATE"]),
                            -4294967296,
                            4294967295,
                        )
                    ),
                    -vm.store.get("motor_speed_" + port_7, 75),
                    stall=vm.store.get("motor_stall_" + port_7, True),
                )
            await multitask_5.await_all()
            # Motor turn for clockwise
            multitask_6 = MultiTask(vm)
            for port_8 in sanitize_ports(vm.vars["PORT_TURNTABLE"]):
                multitask_6.store_task(
                    "motor_laststatus_" + port_8,
                    vm.system.motors.on_port(port_8).run_for_degrees,
                    round(clamp(to_number(vm.vars["OVER_ROTATE"]), -4294967296, 4294967295)),
                    vm.store.get("motor_speed_" + port_8, 75),
                    stall=vm.store.get("motor_stall_" + port_8, True),
                )
            await multitask_6.await_all()
        else:
            # Motor turn for clockwise
            multitask_7 = MultiTask(vm)
            for port_9 in sanitize_ports(vm.vars["PORT_TURNTABLE"]):
                multitask_7.store_task(
                    "motor_laststatus_" + port_9,
                    vm.system.motors.on_port(port_9).run_for_degrees,
                    round(
                        clamp(
                            (to_number(proc_11_quarter_turn_count) * (90 * to_number(vm.vars["TURNTABLE_RATIO"])))
                            + to_number(vm.vars["OVER_ROTATE"]),
                            -4294967296,
                            4294967295,
                        )
                    ),
                    vm.store.get("motor_speed_" + port_9, 75),
                    stall=vm.store.get("motor_stall_" + port_9, True),
                )
            await multitask_7.await_all()
            # Motor turn for counterclockwise
            multitask_8 = MultiTask(vm)
            for port_10 in sanitize_ports(vm.vars["PORT_TURNTABLE"]):
                multitask_8.store_task(
                    "motor_laststatus_" + port_10,
                    vm.system.motors.on_port(port_10).run_for_degrees,
                    round(clamp(to_number(vm.vars["OVER_ROTATE"]), -4294967296, 4294967295)),
                    -vm.store.get("motor_speed_" + port_10, 75),
                    stall=vm.store.get("motor_stall_" + port_10, True),
                )
            await multitask_8.await_all()
        # Procedures call
        await proc_7(vm, stack)
    else:
        # Control if else
        if compare(proc_11_clockwise, "True") == 0:
            # Motor turn for counterclockwise
            multitask_9 = MultiTask(vm)
            for port_11 in sanitize_ports(vm.vars["PORT_TURNTABLE"]):
                multitask_9.store_task(
                    "motor_laststatus_" + port_11,
                    vm.system.motors.on_port(port_11).run_for_degrees,
                    round(
                        clamp(
                            to_number(proc_11_quarter_turn_count) * (90 * to_number(vm.vars["TURNTABLE_RATIO"])),
                            -4294967296,
                            4294967295,
                        )
                    ),
                    -vm.store.get("motor_speed_" + port_11, 75),
                    stall=vm.store.get("motor_stall_" + port_11, True),
                )
            await multitask_9.await_all()
        else:
            # Motor turn for clockwise
            multitask_10 = MultiTask(vm)
            for port_12 in sanitize_ports(vm.vars["PORT_TURNTABLE"]):
                multitask_10.store_task(
                    "motor_laststatus_" + port_12,
                    vm.system.motors.on_port(port_12).run_for_degrees,
                    round(
                        clamp(
                            to_number(proc_11_quarter_turn_count) * (90 * to_number(vm.vars["TURNTABLE_RATIO"])),
                            -4294967296,
                            4294967295,
                        )
                    ),
                    vm.store.get("motor_speed_" + port_12, 75),
                    stall=vm.store.get("motor_stall_" + port_12, True),
                )
            await multitask_10.await_all()


# Procedures definition
async def proc_12(vm, stack):
    # Motor set speed
    for port_13 in sanitize_ports(vm.vars["PORT_COLORARM"]):
        vm.store["motor_speed_" + port_13] = round(clamp(to_number(vm.vars["SPEED_COLORARM"]), -100, 100))
    # Motor set speed
    for port_14 in sanitize_ports(vm.vars["PORT_FLIPPER"]):
        vm.store["motor_speed_" + port_14] = round(clamp(to_number(vm.vars["SPEED_FLIPPER"]), -100, 100))
    # Motor set speed
    for port_15 in sanitize_ports(vm.vars["PORT_TURNTABLE"]):
        vm.store["motor_speed_" + port_15] = round(clamp(to_number(vm.vars["SPEED_TURNTABLE"]), -100, 100))
    # Motor go direction to position
    multitask_11 = MultiTask(vm)
    for port_16 in sanitize_ports(vm.vars["PORT_COLORARM"]):
        multitask_11.store_task(
            "motor_laststatus_" + port_16,
            vm.system.motors.on_port(port_16).run_go_direction_to_position,
            0,
            abs(vm.store.get("motor_speed_" + port_16, 75)),
            "shortest",
            stall=vm.store.get("motor_stall_" + port_16, True),
        )
    await multitask_11.await_all()
    # Motor go direction to position
    multitask_12 = MultiTask(vm)
    for port_17 in sanitize_ports(vm.vars["PORT_FLIPPER"]):
        multitask_12.store_task(
            "motor_laststatus_" + port_17,
            vm.system.motors.on_port(port_17).run_go_direction_to_position,
            0,
            abs(vm.store.get("motor_speed_" + port_17, 75)),
            "shortest",
            stall=vm.store.get("motor_stall_" + port_17, True),
        )
    await multitask_12.await_all()
    # Motor go direction to position
    multitask_13 = MultiTask(vm)
    for port_18 in sanitize_ports(vm.vars["PORT_FLIPPER"]):
        multitask_13.store_task(
            "motor_laststatus_" + port_18,
            vm.system.motors.on_port(port_18).run_go_direction_to_position,
            345,
            abs(vm.store.get("motor_speed_" + port_18, 75)),
            "counterclockwise",
            stall=vm.store.get("motor_stall_" + port_18, True),
        )
    await multitask_13.await_all()
    # Data setvariableto
    vm.vars["SPEED_FLIPPER"] = "50"
    # Motor set speed
    for port_19 in sanitize_ports(vm.vars["PORT_FLIPPER"]):
        vm.store["motor_speed_" + port_19] = round(clamp(to_number(vm.vars["SPEED_FLIPPER"]), -100, 100))
    # Motor stop
    for port_20 in sanitize_ports(vm.vars["PORT_FLIPPER"]):
        vm.system.motors.on_port(port_20).hold()
    # Motor stop
    for port_21 in sanitize_ports(vm.vars["PORT_COLORARM"]):
        vm.system.motors.on_port(port_21).hold()


# Procedures definition
async def proc_13(vm, stack):
    # Data setvariableto
    vm.vars["PORT_COLORARM"] = "D"
    # Data setvariableto
    vm.vars["PORT_COLORSENSOR"] = "B"
    # Data setvariableto
    vm.vars["PORT_FLIPPER"] = "A"
    # Data setvariableto
    vm.vars["PORT_TOUCHSENSOR"] = "F"
    # Data setvariableto
    vm.vars["PORT_TURNTABLE"] = "C"
    # Data setvariableto
    vm.vars["SPEED_COLORARM"] = "20"
    # Data setvariableto
    vm.vars["SPEED_FLIPPER"] = "15"
    # Data setvariableto
    vm.vars["SPEED_TURNTABLE"] = "20"
    # Data setvariableto
    vm.vars["COLORARM_MIDDLE"] = "140"
    # Data setvariableto
    vm.vars["COLORARM_CORNER"] = "270"
    # Data setvariableto
    vm.vars["COLORARM_EDGE"] = "225"
    # Data setvariableto
    vm.vars["COLORARM_HOME"] = "0"
    # Data setvariableto
    vm.vars["TURNTABLE_RATIO"] = "1.4"
    # Data deletealloflist
    vm.lists["colors"].clear()
    # Data deletealloflist
    vm.lists["scan_displays"].clear()
    # Data addtolist
    vm.lists["scan_displays"].append("0000005550059500555000000")
    # Data addtolist
    vm.lists["scan_displays"].append("0000005550055900555000000")
    # Data addtolist
    vm.lists["scan_displays"].append("0000005590055500555000000")
    # Data addtolist
    vm.lists["scan_displays"].append("0000005950055500555000000")
    # Data addtolist
    vm.lists["scan_displays"].append("0000009550055500555000000")
    # Data addtolist
    vm.lists["scan_displays"].append("0000005550095500555000000")
    # Data addtolist
    vm.lists["scan_displays"].append("0000005550055500955000000")
    # Data addtolist
    vm.lists["scan_displays"].append("0000005550055500595000000")
    # Data addtolist
    vm.lists["scan_displays"].append("0000005550055500559000000")


# Procedures definition
async def proc_14(vm, stack, proc_14_colors_to_display):
    # Data setvariableto
    vm.vars["x"] = "1"
    # Control repeat
    for _ in range(9):
        # Led image
        index_4 = int(to_number(vm.vars["x"])) - 1
        if 0 <= index_4 < len(vm.lists["scan_displays"]):
            item_4 = vm.lists["scan_displays"][index_4]
        else:
            item_4 = ""
        vm.system.display.show(hub.Image(convert_image(item_4, vm.store.get("display_brightness", 100))), clear=False)
        # Procedures call
        index_5 = int(to_number(vm.vars["x"])) - 1
        if 0 <= index_5 < len(vm.lists["colors"]):
            item_5 = vm.lists["colors"][index_5]
        else:
            item_5 = ""
        await proc_15(vm, stack, item_5)
        # Control wait
        await sleep_ms(1000)
        # Data changevariableby
        vm.vars["x"] = str(to_number(vm.vars["x"]) + 1)
        yield


# Procedures definition
async def proc_15(vm, stack, proc_15_square_color):
    # Control if
    if compare(proc_15_square_color, "9") == 0:
        # Center button light
        hub.led(*number_color_to_rgb(9))
    # Control if
    if compare(proc_15_square_color, "-1") == 0:
        # Center button light
        hub.led(*number_color_to_rgb(0))
    # Control if
    if compare(proc_15_square_color, "5") == 0:
        # Center button light
        hub.led(*number_color_to_rgb(5))
    # Control if
    if (compare(proc_15_square_color, "3") == 0) or (compare(proc_15_square_color, "4") == 0):
        # Center button light
        hub.led(*number_color_to_rgb(3))
    # Control if
    if compare(proc_15_square_color, "10") == 0:
        # Center button light
        hub.led(*number_color_to_rgb(10))
    # Control if
    if compare(proc_15_square_color, "7") == 0:
        # Center button light
        hub.led(*number_color_to_rgb(7))


def setup(rpc, system):
    vm = VirtualMachine(rpc, system, "MvS6VQhsi2GID_0PB5BP")

    vm.vars["CUBE_ICON"] = "0055509995099950999000000"
    vm.vars["PORT_FLIPPER"] = "A"
    vm.vars["PORT_COLORARM"] = "D"
    vm.vars["PORT_TURNTABLE"] = "C"
    vm.vars["PORT_COLORSENSOR"] = "B"
    vm.vars["SPEED_TURNTABLE"] = "20"
    vm.vars["SPEED_FLIPPER"] = "50"
    vm.vars["x"] = "6"
    vm.vars["OVER_ROTATE"] = "12"
    vm.vars["current_color"] = "0"
    vm.lists["colors"] = []
    vm.lists["scan_displays"] = [
        "0000005550059500555000000",
        "0000005550055900555000000",
        "0000005590055500555000000",
        "0000005950055500555000000",
        "0000009550055500555000000",
        "0000005550095500555000000",
        "0000005550055500955000000",
        "0000005550055500595000000",
        "0000005550055500559000000",
    ]

    vm.register_on_start("Qee!s1b#4Zu#Q%Sk}Zgo", stack_1)

    return vm
