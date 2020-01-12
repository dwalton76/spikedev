# spikedev
A micropython library for LEGO SPIKE.

# micropython development workflow
When you write a SPIKE program in Scratch it is converted to micropython for execution on the SPIKE hub.  It is possible to bypass Scratch and write programs in micropython.  We will walk through the workflow steps in a minute but first some context so the steps make sense.

When SPIKE boots it runs a micropython program called `main.py`.  This is the program that draws the heart, cycles through your programs in slots 0-19 when you press left/right, etc. It also receives programs from the SPIKE app on your laptop via USB or bluetooth.  I haven't had time to dig into the protocol it uses for laptop <-> SPIKE communication so long term that is an option but for now we are going with a different approach. We will be using a program called `ampy` to transfer files to/from SPIKE.  As long as `main.py` is running though `ampy` cannot do anything with the SPIKE filesystem.

## Initial setup
The first order of business is to give ourselves an easy way to exit `main.py`. You should only need to do these steps once (thankfully).

### Manually stop `main.py`
We must access the REPL prompt and ctrl-C `main.py`. To access the REPL prompt use `screen`
```bash
sudo screen /dev/ttyACM0
```

You will see output like the following that is constantly updating
```
{m:0,"p":[[], [61, [0, null]], [], [], [], [], [-20, -24, 999], [2, 5, -2], [18, 1, -1]]}]}}}}]}}}}
```

Press `ctrl-C` and maybe `ctrl-B`, you should see something like the following.
```
MicroPython v1.9.3-1767-g1a6b45250 on 2019-05-23; LEGO Technic Large Hub with STM32F413xx]]}36, 100]}
Type "help()" for more information.
>>>
```

Now you need to exit `screen`, to do that press `ctrl-A` followed by `\`.  It will prompt you with `Really quit and kill all your windows [y/n]` choose `y`

### push `spike-exit-main.py` to slot 19
We copy a one line program (to slot 19) that gives us a way to exit SPIKE's main.py UI.
```bash
sudo ./utils/spike-push-file-to-slot.py utils/spike-exit-main.py 19
```

From now on we will run this program in slot 19 to force `main.py` to exit and allow `ampy` to work its magic.

## Workflow steps
### Write your program
Write your micropython program on your laptop. Here is basic hello world program, named hello-world.py
```micropython
import hub
print("Hello World")
print(hub.info())
```

### Run your program
If the SPIKE UI is running, run the program in slot 19 to exit the UI. Then run your hello-world.py
```bash
sudo ampy --port /dev/ttyACM0 run hello-world.py
```

