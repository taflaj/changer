#! /usr/bin/env python3

# main.py

import logging, sys
from typing import Final

from modules.changer import Changer


VERSION: Final[str] = '1.2.3'


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(lineno)03d %(message)s')
    logging.basicConfig(level=logging.INFO, filename='/tmp/changer.log', format='%(asctime)s %(levelname)-8s %(message)s')
    changer = Changer(sys.argv[0])
    changer.start(VERSION)
