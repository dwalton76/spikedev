# third party libraries
from util.sensors import get_sensor_value

# spikedev libraries
from runtime import VirtualMachine
from uasyncio.core import sleep_ms


# When program starts
async def stack_1(vm, stack):
    # Wait until pressed
    await vm.system.callbacks.custom_sensor_callbacks.until_force_bumped("F")
    # Beep for time
    await vm.system.sound.beep_async(64, 200)
    # Wait until pressed
    while True:
        if get_sensor_value("F", 1, 0, (63,)) == 1:
            break
        await sleep_ms(50)
    # Beep for time
    await vm.system.sound.beep_async(60, 200)
    # Control if
    if get_sensor_value("F", 1, 0, (63,)) == 1:
        # Beep for time
        await vm.system.sound.beep_async(69, 200)


def setup(rpc, system):
    vm = VirtualMachine(rpc, system, "c6UJ-LWeigCyqP6F0MDX")

    vm.register_on_start("uf5T{VXcu]Z)S~i},|VA", stack_1)

    return vm
