#!/usr/bin/env python3

"""
Copy SPIKE's filesystem to a local directory
"""

# standard libraries
import argparse
import grp
import logging
import os
import pwd
import subprocess
import sys
from pprint import pformat
from typing import List, Tuple

log = logging.getLogger(__name__)


def get_directories_and_files(dev: str, path: str) -> Tuple[List, List]:
    """
    Recursively walk the filesystem starting at 'path' and return a list
    of directories and a list of files
    """
    log.info(f"ls {path}")
    files = []
    directories = []
    output = subprocess.check_output(f"ampy --port {dev} ls {path}", shell=True).decode("utf-8")

    for line in output.splitlines():
        if "." in line or "sounds" in path:
            files.append(os.path.join(path, line))
        else:
            directories.append(os.path.join(path, line))

    original_directories = directories[:]

    for directory in original_directories:
        (recursive_directories, recursive_files) = get_directories_and_files(dev, directory)
        directories.extend(recursive_directories)
        files.extend(recursive_files)

    return (directories, files)


def spike_copy_filesystem(dev: str, destination: str) -> bool:
    """
    Copy SPIKE's filesystem to 'destination'
    """

    # ampy requires root perms
    if os.geteuid() != 0:
        log.error("You must run this program using 'sudo'")
        return False

    if not os.path.exists(dev):
        return f"device '{dev}' is not connected"

    if not destination:
        log.error(f"'{destination}' is invalid")
        return False

    if os.path.exists(destination):
        log.error(f"'{destination}' already exist, please rm it")
        return False

    (directories, files) = get_directories_and_files(dev, "/")

    log.info(f"DIRECTORIES\n" + pformat(directories))
    log.info("FILES\n" + pformat(files))

    username = os.environ["SUDO_USER"]
    uid = pwd.getpwnam(username).pw_uid
    gid = grp.getgrnam(username).gr_gid

    for directory in directories:
        dirname = destination + directory
        log.info(f"mkdir {dirname}")
        os.makedirs(dirname)
        os.chown(dirname, uid, gid)

    for filename in files:

        # ampy barfs on the sound files so skip for now
        if "sound" in filename:
            continue

        if filename.endswith(".mpy"):
            continue

        log.info(f"get {filename}")
        target_filename = destination + filename
        subprocess.check_output(f"ampy --port {dev} get {filename} > {target_filename}", shell=True)
        subprocess.check_output(f"dos2unix {target_filename}", shell=True)
        subprocess.check_output(f"dos2unix {target_filename}", shell=True)
        subprocess.check_output(f"dos2unix {target_filename}", shell=True)
        os.chown(target_filename, uid, gid)

    return True


if __name__ == "__main__":

    # configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)16s %(levelname)8s: %(message)s")
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=str, help="Directory to dump filesystem too")
    parser.add_argument("--dev", type=str, default="/dev/ttyACM0", help="/dev/ttyXXXXX of SPIKE")
    args = parser.parse_args()

    if not spike_copy_filesystem(args.dev, args.destination):
        sys.exit(1)
