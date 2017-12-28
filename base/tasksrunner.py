#!/usr/bin/python
# #### #!c:/Python26/ArcGIS10.0/python.exe
# -*- coding: utf-8 -*-
# COPYRIGHT 2016 igsnrr
#
# MORE INFO ...
# email:
"""TasksRunner is designed as the user interface and main entry to
execute specific tools."""

import sys
import argparse
from surfmonthly2bystationtool import SurfMonthly2ByStationTool
from stationhistorytool import StationHistoryTool
from grads2arcgistool import Grads2ArcGisConverterTool
from grid2seriestool import Grid2SeriesConverterTool

from logger import Logger


class TasksRunner:
    """TasksRunner is designed as the user interface and main entry to execute
    specific tools.
    """
    def __init__(self):
        print("Init TasksRunner")
        self._version = "Tasks Runner 0.0.1"
        self._usagemessages = []
        self._tasks = {}
        self._parser = argparse.ArgumentParser(
            prog="python.exe tasksrunner.py",
            description="Tasks Runner Usage Guide.",
            prefix_chars="-+/")
        self._parser.add_argument("--version",
                                  action="version",
                                  version='%(prog)s 0.0.1')
        self._logger = Logger("./log/tasksrunner.log")

    def setupTools(self):
        self._workspace = "C:/Users/hurricane/Documents/GitHub/sda_tools/data/"

        self._subparsers = self._parser.add_subparsers(dest="toolcommand",
                                                       help='Tools')

        # setup and config tools according to config file or UI

        # sample: A list command
        # list_parser = subparsers.add_parser('list', help='List contents')
        # list_parser.add_argument('dirname', action='store',
        #                           help='Directory to list')

        tool = SurfMonthly2ByStationTool()
        self.addTask(tool)

        tool = StationHistoryTool()
        self.addTask(tool)

        tool = Grads2ArcGisConverterTool()
        self.addTask(tool)

        tool = Grid2SeriesConverterTool()
        self.addTask(tool)

    def addTask(self, tool):
        tool.attachLogger(self._logger)
        parser = self._subparsers.add_parser(tool.getName(),
                                             help=tool.getDescription())
        tool.defineArgumentParser(parser)

        self._tasks[tool.getName()] = tool

    def doTasks(self):
        # for (key, tool) in self._tasks.items():
        #     tool.run()
        args = self._parser.parse_args()
        print("The selected tool is: {0}".format(args.toolcommand))
        tool = self._tasks[args.toolcommand]
        tool.run(args)

    def displayUsage(self):
        for msg in self._usagemessages:
            print(msg)

    def displayVersion(self):
        print(self._version)


def main(argv):
    tksRunner = TasksRunner()
    tksRunner.setupTools()
    tksRunner.doTasks()


if __name__ == "__main__":
    main(sys.argv)
else:
    print("loading TaskRunner module")
