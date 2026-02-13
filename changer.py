#! /usr/bin/env -S python3 -OO

# main.py

import argparse
import logging
import sys
from typing import Final

from modules.changer import COPYRIGHT, Changer

VERSION: Final[str] = "26.02.0"
NAME: Final[str] = "changer"


def parse() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(prog=NAME)
    parser.add_argument(
        "command",
        help=f"command to execute (run '{sys.argv[0]} commands' to see the list of available commands)",
    )
    default_config = "./changer.json"
    parser.add_argument(
        "-c",
        "--config",
        help=f"configuration file (default={default_config})",
        default=default_config,
    )
    parser.add_argument(
        "-d", "--debug", help="enable debugging mode", action="store_true"
    )
    parser.add_argument(
        "-v",
        "--version",
        help=f"says this is version {VERSION}",
        action="version",
        version=f"{NAME} {VERSION} - {COPYRIGHT}",
    )
    args, extra = parser.parse_known_args()
    return args, extra


if __name__ == "__main__":
    args, extra = parse()
    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)-8s %(filename)-10s %(lineno)03d %(message)s",
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            filename="/tmp/changer.log",
            format="[%(levelname).1s %(asctime)s] %(message)s",
        )
    changer = Changer(sys.argv[0], args, extra)
    changer.start(VERSION)
