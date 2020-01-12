#!/usr/bin/env python3

"""
Print a table of the programs on SPIKE
"""

# standard libraries
import argparse
import logging
import os
import random
import string
import subprocess
import sys

# third party libraries
from tabulate import tabulate

log = logging.getLogger(__name__)


def indent(data: str, spaces: int) -> str:
    """
    Indent every line in 'data' by 'spaces'
    """
    result = []

    for line in data.splitlines():
        result.append(" " * spaces + line)

    return "\n".join(result)


def spike_slots(dev: str) -> str:
    """
    Return a table of the programs on SPIKE
    """
    SLOTS_FILENAME = "slots." + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # ampy requires root perms
    if os.geteuid() != 0:
        log.error("You must run this program using 'sudo'")
        return False

    if not os.path.exists(dev):
        log.error(f"device '{dev}' is not connected")
        return False

    # get the current .slots file
    subprocess.check_output(f"ampy --port {dev} get projects/.slots > {SLOTS_FILENAME}", shell=True)

    with open(SLOTS_FILENAME, "r") as fh:
        slots = eval(fh.read())
    os.unlink(SLOTS_FILENAME)

    # build the table
    rows = []
    for slot_id in sorted(slots.keys()):
        value = slots[slot_id]
        rows.append([str(slot_id), value["name"], str(value["id"]), str(value["size"])])

    table = tabulate(rows, headers=("slot", "description", "id", "size"))

    # Add leading/trailing blank lines and indent the table by 2 spaces
    print("\n" + indent(table, 2) + "\n")
    return True


if __name__ == "__main__":

    # configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)16s %(levelname)8s: %(message)s")
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", type=str, default="/dev/ttyACM0", help="/dev/ttyXXXXX of SPIKE")
    args = parser.parse_args()

    if not spike_slots(args.dev):
        sys.exit(1)
