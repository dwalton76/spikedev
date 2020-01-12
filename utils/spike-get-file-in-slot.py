#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2019 Daniel Walton <dwalton76@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
Get a micropython file to one of SPIKE's program slots
"""

import argparse
import grp
import logging
import os
import pwd
import random
import string
import subprocess
import sys


log = logging.getLogger(__name__)

MIN_SLOT = 0
MAX_SLOT = 19


def spike_get_file_in_slot(dev: str, target_slot: int) -> bool:
    """
    'cat' a file to one of SPIKE's program slots
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

    # get the current .slots file
    SLOTS_FILENAME = "slots." + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    subprocess.check_output(f"ampy --port {dev} get projects/.slots > {SLOTS_FILENAME}", shell=True)

    with open(SLOTS_FILENAME, "r") as fh:
        slots = eval(fh.read())
    os.unlink(SLOTS_FILENAME)

    if target_slot in slots:
        filename = slots[target_slot]["name"] + ".py"
        file_id = slots[target_slot]["id"]
        subprocess.check_output(f"ampy --port {dev} get projects/{file_id}.py > '{filename}'", shell=True)

        # Remove ^M characters
        subprocess.check_output(f"dos2unix '{filename}'", shell=True)
        subprocess.check_output(f"dos2unix '{filename}'", shell=True)

        # chown the file so the user running this script owns it instead of root
        username = os.environ["SUDO_USER"]
        uid = pwd.getpwnam(username).pw_uid
        gid = grp.getgrnam(username).gr_gid
        os.chown(filename, uid, gid)

        log.info(f"file {file_id} in slot {target_slot} saved as '{filename}'")
        return True
    else:
        log.error(f"no file in slot {target_slot}")
        return False


if __name__ == "__main__":

    # configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)16s %(levelname)8s: %(message)s")
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument("slot", type=int, help=f"SPIKE program slot ({MIN_SLOT}-{MAX_SLOT})")
    parser.add_argument("--dev", type=str, default="/dev/ttyACM0", help="/dev/ttyXXXXX of SPIKE")
    args = parser.parse_args()

    if not spike_get_file_in_slot(args.dev, args.slot):
        sys.exit(1)
