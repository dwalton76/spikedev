===============
REPL Connection
===============

Ubuntu
======

USB
---
::

    sudo screen /dev/ttyACM0
    MicroPython v1.10-1527-g865e961de on 2020-01-23; LEGO Technic Large Hub with STM32F413xx
    Type "help()" for more information.
    >>> {"m":0,"p":[[49, [0, 0, -169, 0]], [61, [99, 7]], [48, [0, 0, 177, 0]], [48, [0, 0, 173, 0]], [49,
    {"m":0,"p":[[49, [0, 0, -169, 0]], [61, [99, 7]], [48, [0, 0, 177, 0]], [48, [0, 0, 172, 0]], [49, [0, {"m":0
    ctrl-C
    >>> import hub

Bluetooth
---------
Use bluetoothctl to enable bluetooth and scanning::

    $ sudo bluetoothctl
    [bluetooth]# agent on
    Agent is already registered
    [bluetooth]# default-agent
    Default agent request successful
    [bluetooth]# scan on
    Discovery started

Press the Bluetooth button on SPIKE, in bluetoothctl you should see something like::

    [NEW] Device 40:BD:32:46:9D:3F 40-BD-32-46-9D-3F
    [CHG] Device 40:BD:32:46:9D:3F Name: LEGO Hub@dwalton76-hub
    [CHG] Device 40:BD:32:46:9D:3F Alias: LEGO Hub@dwalton76-hub

Now pair with that device::

    [bluetooth]# pair 40:BD:32:46:9D:3F
    Attempting to pair with 40:BD:32:46:9D:3F
    [CHG] Device 40:BD:32:46:9D:3F Connected: yes
    [CHG] Device 40:BD:32:46:9D:3F Modalias: bluetooth:v0397p0001d0001
    [CHG] Device 40:BD:32:46:9D:3F UUIDs: 00000000-deca-fade-deca-deafdecacaff
    [CHG] Device 40:BD:32:46:9D:3F UUIDs: 00001101-0000-1000-8000-00805f9b34fb
    [CHG] Device 40:BD:32:46:9D:3F UUIDs: 00001200-0000-1000-8000-00805f9b34fb
    [CHG] Device 40:BD:32:46:9D:3F ServicesResolved: yes
    [CHG] Device 40:BD:32:46:9D:3F Paired: yes
    Pairing successful
    [CHG] Device 40:BD:32:46:9D:3F ServicesResolved: no
    [CHG] Device 40:BD:32:46:9D:3F Connected: no

List your paired devices::

    [bluetooth]# paired-devices
    Device 40:BD:32:46:9D:3F LEGO Hub@dwalton76-hub
    [bluetooth]#

Not sure if it is needed but you can "trust" the hub::

    [bluetooth]# trust 40:BD:32:46:9D:3F
    [CHG] Device 40:BD:32:46:9D:3F Trusted: yes
    Changing 40:BD:32:46:9D:3F trust succeeded
    [bluetooth]#

info about the bluetooth connection::

    [bluetooth]# info 40:BD:32:46:9D:3F
    Device 40:BD:32:46:9D:3F (public)
            Name: LEGO Hub@dwalton76-hub
            Alias: LEGO Hub@dwalton76-hub
            Class: 0x00000804
            Paired: yes
            Trusted: yes
            Blocked: no
            Connected: no
            LegacyPairing: no
            UUID: Vendor specific           (00000000-deca-fade-deca-deafdecacaff)
            UUID: Serial Port               (00001101-0000-1000-8000-00805f9b34fb)
            UUID: PnP Information           (00001200-0000-1000-8000-00805f9b34fb)
            Modalias: bluetooth:v0397p0001d0001
            RSSI: -35
            TxPower: 0

Exit out of bluetoothctl and use rfcomm to create a /dev/rfcomm0 device::

    $ sudo rfcomm bind 0 40:BD:32:46:9D:3F
    $ ls -l /dev/rfcomm0
    crw-rw---- 1 root dialout 216, 0 May  3 08:15 /dev/rfcomm0
    $

Use screen to connect to /dev/rfcomm0::

    $ screen /dev/rfcomm0
    MicroPython v1.10-1527-g865e961de on 2020-01-23; LEGO Technic Large Hub with STM32F413xx
    Type "help()" for more information.
    >>> {"m":0,"p":[[49, [0, 0, -169, 0]], [61, [99, 7]], [48, [0, 0, 177, 0]], [48, [0, 0, 173, 0]], [49,
    {"m":0,"p":[[49, [0, 0, -169, 0]], [61, [99, 7]], [48, [0, 0, 177, 0]], [48, [0, 0, 172, 0]], [49, [0, {"m":0
    ctrl-C
    >>> import hub


Windows 10
==========

USB
---
TBD

Bluetooth
---------
TBD


Mac
===

USB
---
TBD

Bluetooth
---------
TBD
