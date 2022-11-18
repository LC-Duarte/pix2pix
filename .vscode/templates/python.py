#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging

LOG_LEVEL = logging.DEBUG
#Basic log config
def setupLogger(name, level = LOG_LEVEL):
    formatter = logging.Formatter(fmt='%(asctime)s %(process)s %(filename)s:%(lineno)d %(levelname)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)
    return logger

log = setupLogger("main")
################################################################################
#START YOUR CODE HERE:
def main():
    log.debug(sys.argv)
    pass

#DON'T Write bellow
if __name__ == "__main__":
    main()