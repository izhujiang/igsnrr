#!C:/Python26/ArcGIS10.0/python.exe
# -*- coding: utf-8 -*-
#COPYRIGHT 2016 igsnrr
#
#MORE INFO ...
#email: 
"""The tool is designed to convert GRADS file to arcgis file format such as arcgis grid file."""
# ######!/usr/bin/python


import sys,os
import shutil
import time
import numpy as np
import arcpy
from toolbase import ToolBase

""""""
class Grads2ArcGisConverterTool(ToolBase):
    
    def __init__(self):
        ToolBase.__init__(self, "Grads2ArcGisConverterTool", "The Grads2ArcGisConverter tool is to convert GRADS file to arcgis file format such as arcgis grid file.")
        self._version = "grads2arcgistool.py 0.0.1"        
    
    def defineArgumentParser(self, parser):        
        parser.add_argument("ctrl", action="store", help="ctrl file for grads files")
        parser.add_argument("source", action="store", help="root dir for source files")
        parser.add_argument("target", action="store", help="root dir for source files")
        parser.add_argument("-i", "--include", dest="include", action="store", help="file for storing valid files list")
        parser.add_argument("-e", "--exclude", dest="exclude", action="store", help="file for storing excluesive files list")

    def run(self, args):
        # print(args)
        ctlPath = args.ctrl
        srcRoot = args.source
        targetRoot = args.target
        inclusiveFilesPath = args.include
        exclusiveFilesPath = args.exclude
    
        self.loadMeta(ctlPath)
        self.batchConvert(srcRoot, targetRoot, inclusiveFilesPath, exclusiveFilesPath)
    

    def loadMeta(self, path):
        list_of_all_the_lines = []
        with open(path) as ctlFile:
            list_of_all_the_lines = ctlFile.readlines()
        for line in list_of_all_the_lines:
            words = line.split()
            if(words[0].lower() == "undef"):
                self._undef = float(words[1])
            elif(words[0].lower() == "options"):
                self._options = words[1]
            elif(words[0].lower() == "xdef"):
                self._col = int(words[1])
                self._xspace = float(words[4])
                self._left = float(words[3]) - self._xspace / 2
                self._right = self._left + (self._col + 1) * self._xspace
            elif(words[0].lower() == "ydef"):
                self._row = int(words[1])
                self._yspace = float(words[4])
                self._bottom = float(words[3]) -  self._yspace / 2
                self._upper = self._bottom + (self._row + 1) * self._yspace
##        print("undef value: {0}".format(self._undef))
##        print("col and row: {0}  {1}".format(self._col, self._row))
##        print("left and right: {0}  {1}".format(self._left, self._right))
##        print("bottom and upper: {0}  {1}".format(self._bottom, self._upper))


    """Exclude the files in the list load from configue file for exclusive items"""            
    def loadBatchFileList(self, srcPathRoot, inclusiveFilesPath=None, exclusiveFilesPath=None):
        self._taskList = []
        if inclusiveFilesPath is None:
            filelist = os.listdir(srcPathRoot)
            for item in filelist:
                if item.endswith(".grd"):
                    self._taskList.append(item)
        else:
            with open(inclusiveFilesPath) as fbo:
                for line in fbo.readlines():  
                 self._taskList.append(line.strip("\n"))
        
        self._taskExclusiveList = []
        if exclusiveFilesPath is None:
            return
        with open(exclusiveFilesPath) as feo:
            for line in feo.readlines():
                self._taskExclusiveList.append(line.strip("\n"))
            
    def batchConvert(self, srcPathRoot, targetPathRoot, inclusiveFileListPath=None, exclusiveFilePath=None):
        self.loadBatchFileList(srcPathRoot, inclusiveFileListPath, exclusiveFilePath)
        if os.path.exists(targetPathRoot) and len(os.listdir(targetPathRoot)) > 0:
            print("The dir of {0} is not empty and will been overrided. (Y)yes/(N)no".format(targetPathRoot))
            ans = raw_input()
            if ans is "" or ans.lower()=="y" or ans.lower()=="yes":
                shutil.rmtree(targetPathRoot,True)
                time.sleep(1)
            else:
                self._logger.info("Failed: {0} has existed and can't been overrided ".format(targetPath))
                return
        if not os.path.exists(targetPathRoot):
            os.makedirs(targetPathRoot)
        
        for item in self._taskList:
            if item not in self._taskExclusiveList:
                srcPath = os.path.join(srcPathRoot, item)
                target = item.split("-")[1]
                targetPath = os.path.join(targetPathRoot, "cr"+target.replace(".grd",""))
                print("converting {0} to {1}" .format(srcPath, targetPath))
                self.convert(srcPath, targetPath)

                targetPath = os.path.join(targetPathRoot, "gr"+target.replace(".grd",""))
                print("converting {0} to {1}" .format(srcPath, targetPath))
                self.convert(srcPath, targetPath,1,"int32")
                
                
    def convert(self, srcPath, targetPath, index=0, needRetype=None):
        if not os.path.exists(srcPath) or not srcPath.endswith(".grd"):
            self._logger.info("Failed: {0} does not existe or not valid grads *.grd file ".format(srcPath))
        try:
            src = np.fromfile(srcPath, dtype=np.float32)
            if(needRetype != None):
                src = src.astype(needRetype)
            data = src.reshape(2, self._row, self._col)
            rain = data[index]
            
            sr = arcpy.SpatialReference()
            sr.factoryCode = 4326
            sr.create()
            
            arcpy.env.outputCoordinateSystem = sr
            rasterBlock = arcpy.NumPyArrayToRaster(rain, arcpy.Point(self._left, self._bottom),
                                                     self._xspace, self._yspace, self._undef)
            # bug: arcpy.NumPyArrayToRaster can"t work with reversal array
            #rasterBlock = arcpy.NumPyArrayToRaster(rev_rain, arcpy.Point(self._left, self._bottom),
            #                                         self._xspace, self._yspace, self._undef) 
            #rasterBlock.save(targetPath)
            arcpy.Flip_management(rasterBlock, targetPath)
            del src
            
        except Exception as e:  
            self._logger.error("Failed: {0} convert to {1}".format(srcPath, targetPath))
            self._logger.info(e)
        else:
            self._logger.info("Success: {0} convert to {1}".format(srcPath, targetPath))
        finally:
            ## clean up
            pass
    
            
if __name__ == "__main__":
    # testing code
    tool = Grads2ArcGisConverterTool()
    # workspace = "C:/Users/hurricane/Documents/GitHub/sda_tools/data/"
    # srcRoot = workspace + "surf"    
    # targetRoot = workspace + "output"
    import argparse
    from logger import Logger
    parser = argparse.ArgumentParser(prog="python.exe grads2arcgistool.py", description="Grads2ArcGisConverterTool Usage Guide", prefix_chars="-+/") 
    parser.add_argument("--version", action="version", version="%(prog)s 0.0.1")
    tool.defineArgumentParser(parser)
    logger = Logger("./log/gac.log")
    tool.attachLogger(logger)
    args = parser.parse_args() 
    # print(args)
    tool.run(args)   

else:
    print("loading Grads2ArcGisConverter module")
