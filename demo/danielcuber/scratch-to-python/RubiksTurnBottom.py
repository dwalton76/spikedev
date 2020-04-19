# third party libraries
from util.scratch import clamp, to_number

# spikedev libraries
from runtime import VirtualMachine


# When program starts
async def stack_1(vm, stack):
    # Data setvariableto
    GEAR_RATIO = 1.4
    quarter_turn_count = 1
    hold_degrees = 140
    rotate_extra = 20

    # Motor set stall detection
    vm.store["motor_stall_C"] = True
    vm.store["motor_speed_C"] = 80
    vm.store["motor_speed_D"] = 70

    # Move colorarm to hold
    # Motor go direction to position
    vm.store["motor_laststatus_D"] = await vm.system.motors.on_port("D").run_go_direction_to_position_async(
        hold_degrees,
        abs(vm.store.get("motor_speed_D", 75)),
        "counterclockwise",
        stall=vm.store.get("motor_stall_D", True),
    )

    # Motor turn for counterclockwise
    vm.store["motor_laststatus_C"] = await vm.system.motors.on_port("C").run_for_degrees_async(
        int((GEAR_RATIO * 90 * quarter_turn_count) + rotate_extra),
        -1 * vm.store.get("motor_speed_C", 75),
        stall=vm.store.get("motor_stall_C", True),
    )

    # Motor turn for clockwise
    vm.store["motor_laststatus_C"] = await vm.system.motors.on_port("C").run_for_degrees_async(
        rotate_extra, vm.store.get("motor_speed_C", 75), stall=vm.store.get("motor_stall_C", True)
    )

    # move colorarm out of the way
    # Motor go direction to position
    vm.store["motor_laststatus_D"] = await vm.system.motors.on_port("D").run_go_direction_to_position_async(
        0, abs(vm.store.get("motor_speed_D", 75)), "clockwise", stall=vm.store.get("motor_stall_D", True)
    )


def setup(rpc, system):
    vm = VirtualMachine(rpc, system, "Target__1")

    vm.store["motor_laststatus_D"] = 0
    vm.store["motor_laststatus_C"] = 0
    vm.store["motor_speed_D"] = 70
    vm.store["motor_speed_C"] = 80
    vm.store["motor_stall_C"] = True
    vm.vars["hold_degrees"] = "140"
    vm.vars["rotate_extra"] = "20"
    vm.vars["GEAR_RATIO"] = "1.4"
    vm.vars["quarter_turn_count"] = "1"

    vm.register_on_start("[rH;-khJ6TUe1g1N#R[R", stack_1)

    return vm
