# -*- coding: utf-8 -*-
#COPYRIGHT 2016 igsnrr
#
#MORE INFO ...
#email: 
"""Tool base and interface for all specific tool."""
# ######!/usr/bin/python

""""""
class ToolBase:    
    def __init__(self, name, description):
        # print("Init ToolBase")
        self._name = name
        self._description = description
        self._version = "toolbase.py 0.0.1"        
        self._params = {}
        self._usagemessages = []

    def getName(self):
        return self._name
    def getDescription(self):
        return self._description
    def getVersion(self):
        return self._version
    def displayVersion(self):
        print(self._version)

    def attachLogger(self, logger):
        self._logger = logger
        
    def setParameter(self, paraName, paraValue):
        self._params[paraName] = paraValue
    
    def run(self, args):
        print("Running Tool: {0}".format(self._name))

    """Todo: """
    def runWithScript(self, script):
        print("Running Tool: {0} with script {1}".format(self._name, script))
        print("parse script and call run function")
    
    """setting up the parser of argument"""
    def defineArgumentParser(self, parser):
        print("define argument parser using parser.add_argument()")    

    def displayUsage(self):
        # Todo: 
        for msg in self._usagemessages:
            print(msg)

    
if __name__ == "__main__":
    tb = ToolBase("BaseTool", "Base class for tools")
    print(tb.getName())
    print(tb.getDescription())
    tb.displayVersion()
    tb.displayUsage()
    tb.run()
    tb.runWithScript("")
else:
    print("loading  toolbase module")
