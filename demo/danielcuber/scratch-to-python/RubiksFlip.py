# third party libraries
from util.scratch import clamp, to_number

# spikedev libraries
from runtime import VirtualMachine


# When program starts
async def stack_1(vm, stack):

    # Data setvariableto
    poker_degrees = 140
    push_center_degreees = 120

    # Motor set speed
    vm.store["motor_speed_A"] = 10

    # Lean back to 347...this goes in init_motors()
    # Motor go direction to position
    vm.store["motor_laststatus_A"] = await vm.system.motors.on_port("A").run_go_direction_to_position_async(
        347, abs(vm.store.get("motor_speed_A", 75)), "counterclockwise", stall=vm.store.get("motor_stall_A", True)
    )

    # Motor set speed
    vm.store["motor_speed_A"] = 60

    # Motor go direction to position
    vm.store["motor_laststatus_A"] = await vm.system.motors.on_port("A").run_go_direction_to_position_async(
        poker_degrees, abs(vm.store.get("motor_speed_A", 75)), "clockwise", stall=vm.store.get("motor_stall_A", True)
    )

    # Motor go direction to position
    vm.store["motor_laststatus_A"] = await vm.system.motors.on_port("A").run_go_direction_to_position_async(
        347, abs(vm.store.get("motor_speed_A", 75)), "counterclockwise", stall=vm.store.get("motor_stall_A", True)
    )

    # Move colorarm forward to nudge cube
    # Motor set speed
    vm.store["motor_speed_D"] = 75

    # Motor go direction to position
    vm.store["motor_laststatus_D"] = await vm.system.motors.on_port("D").run_go_direction_to_position_async(
        push_center_degrees,
        abs(vm.store.get("motor_speed_D", 75)),
        "counterclockwise",
        stall=vm.store.get("motor_stall_D", True),
    )

    # Motor set speed
    vm.store["motor_speed_D"] = 75

    # Motor go direction to position
    vm.store["motor_laststatus_D"] = await vm.system.motors.on_port("D").run_go_direction_to_position_async(
        0, abs(vm.store.get("motor_speed_D", 75)), "clockwise", stall=vm.store.get("motor_stall_D", True)
    )


def setup(rpc, system):
    vm = VirtualMachine(rpc, system, "Target__1")

    vm.store["motor_laststatus_A"] = 0
    vm.store["motor_laststatus_D"] = 0
    vm.store["motor_speed_A"] = 60
    vm.store["motor_speed_D"] = 20
    vm.vars["poker_degrees"] = "140"
    vm.vars["push_center_degreees"] = "120"

    vm.register_on_start("Ud_M2Y?cJAODx1}$t7!c", stack_1)

    return vm
