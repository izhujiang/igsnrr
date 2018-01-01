#!c:/Python26/ArcGIS10.0/python.exe
# -*- coding: utf-8 -*-
#COPYRIGHT 2016 igsnrr
#
#MORE INFO ...
#email:
"""The statistics tool for station's history."""
# ######!/usr/bin/python

import sys,os
import re
import shutil
from toolbase import ToolBase
""""""
class StationHistoryTool(ToolBase):
    def __init__(self):
        ToolBase.__init__(self, "StationHistoryTool", "The statistics tool for station's history.")
        self._version = "stationhistorytool.py 0.0.1"


    def defineArgumentParser(self, parser):
        parser.add_argument('source', action='store', help="root dir for source files")
        parser.add_argument('target', action='store', help="target file for statistics result")

    def run(self, args):
        print("Running Tool: {0}".format(self._name))
        if args.source is not None and args.target is not None:
            self._srcPathRoot  = args.source
            self._targetPath = args.target

            if not os.path.exists(os.path.dirname(self._targetPath)):
                os.makedirs(os.path.dirname(self._targetPath))

            if os.path.dirname(self._targetPath) == self._srcPathRoot:
                logger.error("Failed: The dir of target file should not be equivalent to source path root.")

            self.batchConvert(self._srcPathRoot, self._targetPath)
        else:
            self._logger.error("Failed: missing source path root or target path root!")


    """ """
    def loadBatchFileList(self, srcPathRoot, filter=None):
        self._taskList = []
        if filter is None:
            for item in os.listdir(srcPathRoot):
                path = os.path.join(srcPathRoot,item)
                if os.path.isfile(path):
                    self._taskList.append(item)
        # print(self._taskList)

    def batchConvert(self, srcPathRoot,  targetPath):
        self.loadBatchFileList(srcPathRoot)

        try:
            with open(targetPath, "w") as tfo:

                for item in self._taskList:
                    srcPath = os.path.join(srcPathRoot, item)
                    print("Processing {0}".format(srcPath))
                    lines = []
                    with open(srcPath) as fo:
                        lines = fo.readlines()

                        minI = -1
                        maxI = -1
                        minD = 99999999
                        maxD = 10000000

                        for i in range(len(lines)):
                            line = lines[i]
                            words = line.split()
                            date = int("{0}{1:0>2}{2}".format(words[4], words[5], words[6]))
                            if date < minD:
                                minD = date
                                minI = i
                            if date > maxD:
                                maxD = date
                                maxI = i

                        line = lines[maxI]
                        words = line.split()
                        sid = words[0]
                        lat = int(words[1])
                        lat = lat/100 + lat%100/float(60)
                        lon = int(words[2])
                        lon = lon/100 + lon%100/float(60)
                        # todo: alt will be processed by some rules
                        alt = words[3]
                        endDate = maxD

                        line = lines[minI]
                        words = line.split()
                        beginDate = minD

                        record = "{0:>8} {1:>8} {2:>8} {3:>8} {4:>12} {5:>12}\n".format(sid, lon, lat, alt, beginDate,endDate)
                        tfo.write(record)
        except Exception as e:
            self._logger.error(e)

if __name__ == "__main__":
    # testing code
    tool = StationHistoryTool()
    # workspace = "C:/Users/hurricane/Documents/GitHub/sda_tools/data/"
    # srcRoot = workspace + "surf"
    # targetRoot = workspace + "output"
    import argparse
    from logger import Logger
    parser = argparse.ArgumentParser(prog="python.exe stationhistorytool.py", description="StationHistoryTool Usage Guide", prefix_chars="-+")
    parser.add_argument("--version", action="version", version='%(prog)s 0.0.1')
    tool.defineArgumentParser(parser)
    logger = Logger("./log/sh.log")
    tool.attachLogger(logger)
    args = parser.parse_args()
    # print(args)
    tool.run(args)

else:
    print("loading  stationhistorytool module")
