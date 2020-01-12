# spikedev
A micropython library for LEGO SPIKE.

# stop the SPIKE UI
The SPIKE UI (heart picture, click left/right to select a program, etc) is produced by a program called `main.py` that runs when the hub boots.  We need to stop `main.py` so that we can run our own micropython programs.

To stop `main.py we must access the REPL (Read Evaluate Print Loop) prompt and ctrl-C `main.py`. To access the REPL prompt on linux we can use the `screen` utility:

```bash
sudo screen /dev/ttyACM0
```

You will see output like the following that is constantly updating
```
{m:0,"p":[[], [61, [0, null]], [], [], [], [], [-20, -24, 999], [2, 5, -2], [18, 1, -1]]}]}}}}]}}}}
```

Press `ctrl-C` followed by`ctrl-B`, you should see something like the following.
```
MicroPython v1.9.3-1767-g1a6b45250 on 2019-05-23; LEGO Technic Large Hub with STM32F413xx]]}36, 100]}
Type "help()" for more information.
>>>
```

Exit `screen` by pressing `ctrl-A` followed by `\`.  It will prompt you with `Really quit and kill all your windows [y/n]`, choose `y`

# Workflow steps
## Write your program
Write your micropython program on your laptop. Here is basic hello-world.py
```micropython
import hub
print("Hello World")
print(hub.info())
```

## Run your program
Use the `ampy` tool to run hello-world.py
```bash
$ sudo ampy --port /dev/ttyACM0 run demo/hello-world/hello-world.py
Hello World
{'1ms_tick_min': 0.0, '1ms_tick_on_time': 99.4973, '1ms_tick_miss': 317, '1ms_tick_max': 1.10068e+09, '1ms_tick_total': 63059, 'hardware_version': 'Version_E', 'device_uuid': '03970000-3400-1900-0551-383138393536'}
$
```
