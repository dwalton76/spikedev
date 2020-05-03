# third party libraries
import hub
from util.scratch import compare, convert_image, to_number

# spikedev libraries
from runtime import VirtualMachine
from uasyncio.core import sleep_ms


# When program starts
async def stack_1(vm, stack):
    # Procedures call
    await proc(vm, stack)


# Procedures definition
async def proc(vm, stack):
    # Data setvariableto
    vm.vars["busy_circle_state"] = "1"
    # Control forever
    while True:
        # Control if
        if compare(vm.vars["busy_circle_state"], "1") == 0:
            # Led image
            vm.system.display.show(
                hub.Image(convert_image("0010000000000000000000000", vm.store.get("display_brightness", 100))),
                clear=False,
            )
        # Control if
        if compare(vm.vars["busy_circle_state"], "2") == 0:
            # Led image
            vm.system.display.show(
                hub.Image(convert_image("0001000000000000000000000", vm.store.get("display_brightness", 100))),
                clear=False,
            )
        # Control if
        if compare(vm.vars["busy_circle_state"], "3") == 0:
            # Led image
            vm.system.display.show(
                hub.Image(convert_image("0000000001000000000000000", vm.store.get("display_brightness", 100))),
                clear=False,
            )
        # Control if
        if compare(vm.vars["busy_circle_state"], "4") == 0:
            # Led image
            vm.system.display.show(
                hub.Image(convert_image("0000000000000010000000000", vm.store.get("display_brightness", 100))),
                clear=False,
            )
        # Control if
        if compare(vm.vars["busy_circle_state"], "5") == 0:
            # Led image
            vm.system.display.show(
                hub.Image(convert_image("0000000000000000000100000", vm.store.get("display_brightness", 100))),
                clear=False,
            )
        # Control if
        if compare(vm.vars["busy_circle_state"], "6") == 0:
            # Led image
            vm.system.display.show(
                hub.Image(convert_image("0000000000000000000000010", vm.store.get("display_brightness", 100))),
                clear=False,
            )
        # Control if
        if compare(vm.vars["busy_circle_state"], "7") == 0:
            # Led image
            vm.system.display.show(
                hub.Image(convert_image("0000000000000000000000100", vm.store.get("display_brightness", 100))),
                clear=False,
            )
        # Control if
        if compare(vm.vars["busy_circle_state"], "8") == 0:
            # Led image
            vm.system.display.show(
                hub.Image(convert_image("0000000000000000000001000", vm.store.get("display_brightness", 100))),
                clear=False,
            )
        # Control if
        if compare(vm.vars["busy_circle_state"], "9") == 0:
            # Led image
            vm.system.display.show(
                hub.Image(convert_image("0000000000000001000000000", vm.store.get("display_brightness", 100))),
                clear=False,
            )
        # Control if
        if compare(vm.vars["busy_circle_state"], "10") == 0:
            # Led image
            vm.system.display.show(
                hub.Image(convert_image("0000000000100000000000000", vm.store.get("display_brightness", 100))),
                clear=False,
            )
        # Control if
        if compare(vm.vars["busy_circle_state"], "11") == 0:
            # Led image
            vm.system.display.show(
                hub.Image(convert_image("0000010000000000000000000", vm.store.get("display_brightness", 100))),
                clear=False,
            )
        # Control if
        if compare(vm.vars["busy_circle_state"], "12") == 0:
            # Led image
            vm.system.display.show(
                hub.Image(convert_image("0100000000000000000000000", vm.store.get("display_brightness", 100))),
                clear=False,
            )
        # Data changevariableby
        vm.vars["busy_circle_state"] = str(to_number(vm.vars["busy_circle_state"]) + 1)
        # Control if
        if compare(vm.vars["busy_circle_state"], "13") == 0:
            # Data setvariableto
            vm.vars["busy_circle_state"] = "1"
        # Control wait
        await sleep_ms(20)
        yield


def setup(rpc, system):
    vm = VirtualMachine(rpc, system)

    vm.vars["busy_circle_state"] = "2118748"

    vm.register_on_start("fn[-+ncXek8jGKh+Qaf%", stack_1)

    return vm
