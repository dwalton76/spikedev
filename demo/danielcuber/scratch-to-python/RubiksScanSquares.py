# third party libraries
import hub
from util.scratch import clamp, number_color_to_rgb, to_number
from util.sensors import get_sensor_value

# spikedev libraries
from runtime import VirtualMachine
from uasyncio.core import sleep_ms


# When program starts
async def stack_1(vm, stack):

    # 120 for center square
    # 210 for edge square
    # 235 for corner square

    # Data setvariableto
    vm.vars["degrees"] = "120"

    # Motor set speed
    vm.store["motor_speed_D"] = 20

    # Motor go direction to position
    vm.store["motor_laststatus_D"] = await vm.system.motors.on_port("D").run_go_direction_to_position_async(
        clamp(to_number(vm.vars["degrees"]), -4294967296, 4294967295),
        abs(vm.store.get("motor_speed_D", 75)),
        "counterclockwise",
        stall=vm.store.get("motor_stall_D", True),
    )

    # Control if
    sensor_value = get_sensor_value("B", 0, -1, (61,))
    if sensor_value is None:
        sensor_value = -1
    if 9 == sensor_value:
        # Center button light
        hub.led(*number_color_to_rgb(9))
    # Control if
    sensor_value_1 = get_sensor_value("B", 0, -1, (61,))
    if sensor_value_1 is None:
        sensor_value_1 = -1
    if 5 == sensor_value_1:
        # Center button light
        hub.led(*number_color_to_rgb(5))
    # Control if
    sensor_value_2 = get_sensor_value("B", 0, -1, (61,))
    if sensor_value_2 is None:
        sensor_value_2 = -1
    if 3 == sensor_value_2:
        # Center button light
        hub.led(*number_color_to_rgb(3))
    # Control if
    sensor_value_3 = get_sensor_value("B", 0, -1, (61,))
    if sensor_value_3 is None:
        sensor_value_3 = -1
    if 10 == sensor_value_3:
        # Center button light
        hub.led(*number_color_to_rgb(10))
    # Control if
    sensor_value_4 = get_sensor_value("B", 0, -1, (61,))
    if sensor_value_4 is None:
        sensor_value_4 = -1
    if 7 == sensor_value_4:
        # Center button light
        hub.led(*number_color_to_rgb(7))
    # Control if
    sensor_value_5 = get_sensor_value("B", 0, -1, (61,))
    if sensor_value_5 is None:
        sensor_value_5 = -1
    if -1 == sensor_value_5:
        # Center button light
        hub.led(*number_color_to_rgb(1))
    # Control wait
    await sleep_ms(3000)

    # Go back to zero
    # Motor go direction to position
    vm.store["motor_laststatus_D"] = await vm.system.motors.on_port("D").run_go_direction_to_position_async(
        0, abs(vm.store.get("motor_speed_D", 75)), "clockwise", stall=vm.store.get("motor_stall_D", True)
    )


def setup(rpc, system):
    vm = VirtualMachine(rpc, system, "Target__1")
    vm.vars["degrees"] = "235"
    vm.register_on_start("V!o?7=)YTAqt(l*2-oz0", stack_1)
    return vm
