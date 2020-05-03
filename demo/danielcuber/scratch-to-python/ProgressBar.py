# third party libraries
import hub
from util.scratch import compare, convert_brightness, convert_image, to_number

# spikedev libraries
from runtime import VirtualMachine
from uasyncio.core import sleep_ms


# When program starts
async def stack_1(vm, stack):
    # Led image
    vm.system.display.show(
        hub.Image(convert_image("0000000000000000000000000", vm.store.get("display_brightness", 100))), clear=False
    )
    # Data setvariableto
    vm.vars["target"] = "22"
    # Procedures call
    # Attempt to call updated procedure with outdated block
    # Procedures call
    # Attempt to call updated procedure with outdated block


# Procedures definition
async def proc(vm, stack, proc_percent, proc_target, proc_interval):
    # Data setvariableto
    vm.vars["x"] = "1"
    # Data setvariableto
    vm.vars["y"] = "5"
    # Data setvariableto
    vm.vars["count"] = "0"
    # Control repeat until
    while not (compare(vm.vars["count"], proc_target) == 0):
        # Led on
        x = int(to_number(vm.vars["x"])) - 1
        y = int(to_number(vm.vars["y"])) - 1
        if (0 <= x < 5) and (0 <= y < 5):
            hub.display.set_pixel(x, y, convert_brightness(to_number(proc_percent)))
        # Data changevariableby
        vm.vars["count"] = str(to_number(vm.vars["count"]) + 1)
        # Data changevariableby
        vm.vars["x"] = str(to_number(vm.vars["x"]) + 1)
        # Control if
        if compare(vm.vars["x"], "6") == 0:
            # Data setvariableto
            vm.vars["x"] = "1"
            # Data changevariableby
            vm.vars["y"] = str(to_number(vm.vars["y"]) + -1)
        # Control if
        if compare(proc_interval, "0.1") == 0:
            # Control wait
            await sleep_ms(100)
        yield


def setup(rpc, system):
    vm = VirtualMachine(rpc, system)

    vm.vars["x"] = "3"
    vm.vars["y"] = "1"
    vm.vars["count"] = "22"
    vm.vars["target"] = "22"

    vm.register_on_start("Y-RLOAU?rL#$`a!dO3oC", stack_1)

    return vm
