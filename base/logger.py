# -*- coding: utf-8 -*-
#COPYRIGHT 2016 igsnrr
#
#MORE INFO ...
#email: 
"""Logger is designed as wrapper of logging."""
# ######!/usr/bin/python

import sys,os
import logging

#define global variables and contants

""""""
class Logger:
    
    def __init__(self, logPath):
        dir = os.path.dirname(logPath)
        if not os.path.exists(dir):
            os.makedirs(dir)

        print("Init Logger")
        _version = "Logger.py 0.0.1"
        logging.basicConfig(level=logging.DEBUG,
                format="%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s",
                datefmt="%a, %d %b %Y %H:%M:%S",
                filename=logPath,
                filemode="w")
        # define StreamHandler#
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
        console.setFormatter(formatter)
        logging.getLogger("").addHandler(console)

    def debug(self, msg):
        logging.debug(msg)
    def info(self, msg):
        logging.info(msg)
    def warning(self, msg):
        logging.warning(msg)
    def error(self, msg):
        logging.error(msg)
    def displayVersion(self):
        print(self._version)       
if __name__ == "__main__":
    log = Logger("./log/sample.log")

    log.debug("This is debug message")
    log.info("This is info message")
    log.warning("This is warning message")
    log.error("This is error message")
else:
    print("loading logger module")
