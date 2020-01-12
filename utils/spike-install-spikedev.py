#!/usr/bin/env python3

"""
Install all spikedev files to a 'spikedev' directory on SPIKE
"""

# standard libraries
import argparse
import grp
import logging
import os
import pwd
import subprocess
import sys
from typing import List

log = logging.getLogger(__name__)


def get_filenames(directory: str) -> List[str]:
    """
    Return a list of filenames in ``directory``
    """
    return [filename for filename in os.listdir(directory) if os.path.isfile(os.path.join(directory, filename))]


def spike_directory_exists(dev: str, directory: str) -> bool:
    """
    Return True if ``directory`` exists on SPIKE, else return False
    """
    cmd = f"ampy --port {dev} ls {directory}"
    log.info(cmd)

    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False


def spike_install_spikedev(dev: str) -> bool:
    """
    Install all spikedev files to a 'spikedev' directory on SPIKE
    """

    # ampy requires root perms
    if os.geteuid() != 0:
        log.error("You must run this program using 'sudo'")
        return False

    if not os.path.exists(dev):
        log.error(f"device '{dev}' is not connected")
        return False

    LOCAL_DIRECTORY = "spikedev"
    REMOTE_DIRECTORY = "spikedev"

    if not spike_directory_exists(dev, REMOTE_DIRECTORY):
        cmd = f"ampy --port {dev} mkdir {REMOTE_DIRECTORY}"
        log.info(cmd)
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)

    # copy every file in our spikedev directory to the spikedev on SPIKE
    for filename in get_filenames(LOCAL_DIRECTORY):

        if filename.endswith(".swp"):
            continue

        cmd = f"ampy --port {dev} put {LOCAL_DIRECTORY}/{filename} {REMOTE_DIRECTORY}/{filename}"
        log.info(cmd)
        subprocess.check_output(cmd, shell=True)

    return True


if __name__ == "__main__":

    # configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)16s %(levelname)8s: %(message)s")
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", type=str, default="/dev/ttyACM0", help="/dev/ttyXXXXX of SPIKE")
    args = parser.parse_args()

    if not spike_install_spikedev(args.dev):
        sys.exit(1)
