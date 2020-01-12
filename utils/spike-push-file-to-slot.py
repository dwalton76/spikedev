#!/usr/bin/env python3

"""
Push a micropython file to one of SPIKE's program slots
"""

# standard libraries
import argparse
import logging
import os
import random
import string
import subprocess
import sys
from pprint import pformat

log = logging.getLogger(__name__)

MIN_SLOT = 0
MAX_SLOT = 19


def spike_push_file_to_slot(dev: str, filename: str, target_slot: int) -> bool:
    """
    Push a micropython file to one of SPIKE's program slots
    """

    # ampy requires root perms
    if os.geteuid() != 0:
        log.error("You must run this program using 'sudo'")
        return False

    if not os.path.exists(dev):
        log.error(f"device '{dev}' is not connected")
        return False

    if target_slot < MIN_SLOT or target_slot > MAX_SLOT:
        log.error(f"invalid target_slot {target_slot} (min {MIN_SLOT}, max {MAX_SLOT})")
        return False

    if not os.path.isfile(filename):
        log.error(f"{filename} does not exist")
        return False

    # get the size of the file we are pushing
    filesize = os.stat(filename).st_size
    created_time = int(os.path.getctime(filename))
    modified_time = int(os.path.getmtime(filename))

    # get the current .slots file
    SLOTS_FILENAME = "slots." + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    subprocess.check_output(f"ampy --port {dev} get projects/.slots > {SLOTS_FILENAME}", shell=True)

    with open(SLOTS_FILENAME, "r") as fh:
        slots = eval(fh.read())

    # Is filename already in that slot? If so use the same ID
    if target_slot in slots and slots[target_slot]["name"] == os.path.basename(filename):
        filename_id = slots[target_slot]["id"]

    # If not delete the old entry in that slot (if there is one) and
    # pick a random ID
    else:

        if target_slot in slots:
            # rm the current program in that slot
            subprocess.check_output(f"ampy --port {dev} rm projects/{slots[target_slot]['id']}.py", shell=True)
            del slots[target_slot]

        # Pick a random ID but make sure we pick one that isn't already
        # used in some other slot
        used_IDs = [x["id"] for x in slots.values()]

        while True:
            filename_id = random.randint(1000000, 9999999999)

            if filename_id not in used_IDs:
                break

    slots[target_slot] = {
        "name": os.path.basename(filename),
        "created": created_time,
        "modified": modified_time,
        "size": filesize,
        "id": filename_id,
    }

    # Write the new .slots file
    with open(SLOTS_FILENAME, "w") as fh:
        fh.write(pformat(slots) + "\n")

    # Copy the new .slots file to SPIKE
    subprocess.check_output(f"sudo ampy --port {dev} put {SLOTS_FILENAME} projects/.slots", shell=True)

    # Copy filename to SPIKE but name it based on its ID
    subprocess.check_output(f"sudo ampy --port {dev} put {filename} projects/{filename_id}.py", shell=True)

    os.unlink(SLOTS_FILENAME)
    return True


if __name__ == "__main__":

    # configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)16s %(levelname)8s: %(message)s")
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="micropython file to push")
    parser.add_argument("slot", type=int, help=f"SPIKE program slot ({MIN_SLOT}-{MAX_SLOT})")
    parser.add_argument("--dev", type=str, default="/dev/ttyACM0", help="/dev/ttyXXXXX of SPIKE")
    args = parser.parse_args()

    if not spike_push_file_to_slot(args.dev, args.filename, args.slot):
        sys.exit(1)
