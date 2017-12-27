#!c:/Python26/ArcGIS10.0/python.exe
# -*- coding: utf-8 -*-
#COPYRIGHT 2016 igsnrr
#
#MORE INFO ...
#email: 
"""The tool is designed to convert surf(surface station observed data) files by month into by station."""
# ######!/usr/bin/python

import sys,os
import re
import shutil
from toolbase import ToolBase
""""""
class SurfMonthly2ByStationTool(ToolBase):
    def __init__(self):
        ToolBase.__init__(self, "SurfMonthly2ByStationTool", "The tool is designed to convert surf(surface station observed data) files by month into by station.")
        self._version = "surfmonthly2bystation.py 0.0.1"
        
    
    def defineArgumentParser(self, parser):        
        parser.add_argument('source', action='store', help="root dir for source files")
        parser.add_argument('target', action='store', help="root dir for target files")

    def run(self, args):
        print("Running Tool: {0}".format(self._name))        
        if args.source is not None and args.target is not None:
            self._srcPathRoot  = args.source
            self._targetPathRoot = args.target
                        
            self.batchConvert(self._srcPathRoot, self._targetPathRoot)
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

    def batchConvert(self, srcPathRoot,  targetPathRoot):
        self.loadBatchFileList(srcPathRoot)
        
        if os.path.exists(targetPathRoot):
            shutil.rmtree(targetPathRoot)
        os.makedirs(targetPathRoot)       
        
        # files = {}
        buf_lines = {}
        try:
            for item in self._taskList:
                srcPath = os.path.join(srcPathRoot, item)
                print("Processing {0}".format(srcPath))
                lines = []
                with open(srcPath) as fo:
                    lines = fo.readlines()
                    for line in lines:
                        words = line.split()                                            

                        if not words[0] in buf_lines.keys():
                            buf_lines[words[0]] = []
                        buf_lines[words[0]].append(line)

                    for (k, slines) in buf_lines.items():
                        fpath = os.path.join(targetPathRoot, k + ".TXT")
                        with open(fpath, "a") as tfo:
                            tfo.writelines(slines)
                            tfo.flush()
                    buf_lines.clear()
        except Exception as e:            
            self._logger.error(e)
        finally:
            pass
            # for (k, fo) in files.items():
            #     fo.close()
            # files.clear()
            
if __name__ == "__main__":
    # testing code
    tool = SurfMonthly2ByStationTool()
    # workspace = "C:/Users/hurricane/Documents/GitHub/sda_tools/data/"
    # srcRoot = workspace + "surf"    
    # targetRoot = workspace + "output"
    import argparse
    from logger import Logger
    parser = argparse.ArgumentParser(prog="python.exe surfmonthly2bystationtool.py", description="SurfMonthly2ByStationTool Usage Guide", prefix_chars="-+/") 
    parser.add_argument("--version", action="version", version='%(prog)s 0.0.1')
    tool.defineArgumentParser(parser)
    logger = Logger("./log/s2st.log")
    tool.attachLogger(logger)
    args = parser.parse_args() 
    # print(args)
    tool.run(args)   

else:
    print("loading  surfmonthly2bystationtool module")
