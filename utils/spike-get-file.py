#!/usr/bin/env python3

"""
Get a micropython file from one of SPIKE's program slots
"""

# standard libraries
import argparse
import grp
import logging
import os
import pwd
import subprocess
import sys

log = logging.getLogger(__name__)


def spike_get_file(dev: str, filename: str) -> bool:
    """
    'cat' the runtime.log file
    """

    # ampy requires root perms
    if os.geteuid() != 0:
        log.error("You must run this program using 'sudo'")
        return False

    if not os.path.exists(dev):
        log.error(f"device '{dev}' is not connected")
        return False

    subprocess.check_output(f"ampy --port {dev} get {filename} > {filename}", shell=True)

    username = os.environ["SUDO_USER"]
    uid = pwd.getpwnam(username).pw_uid
    gid = grp.getgrnam(username).gr_gid
    os.chown(filename, uid, gid)

    with open(filename, "r") as fh:
        print(fh.read())

    return True


if __name__ == "__main__":

    # configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)16s %(levelname)8s: %(message)s")
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", type=str, default="/dev/ttyACM0", help="/dev/ttyXXXXX of SPIKE")
    parser.add_argument("--filename", type=str, default="runtime.log")
    args = parser.parse_args()

    if not spike_get_file(args.dev, args.filename):
        sys.exit(1)
