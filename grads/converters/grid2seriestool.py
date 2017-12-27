#!c:/Python26/ArcGIS10.0/python.exe
# -*- coding: utf-8 -*-
#COPYRIGHT 2016 igsnrr
#
#MORE INFO ...
#email:
"""The tool is designed to convert Arcgis Grid file to Series."""
# ######!/usr/bin/python


import sys,os
import numpy as np
import arcpy
from arcpy.sa import *
from arcpy import env
import shutil
import time
from toolbase import ToolBase
from series import SeriesWithLocation

"""Tool for Converting ESRI Grid Fiels to Series"""
class Grid2SeriesConverterTool(ToolBase):
    def __init__(self):
        ToolBase.__init__(self, "Grid2SeriesConverterTool", "The Grid2SeriesConverterTool is to convert Arcgis grd file to series flat files.")
        self._version = "grid2seriestool.py 0.0.1"

    def defineArgumentParser(self, parser):
        parser.add_argument("source", action="store", help="root dir for source files")
        parser.add_argument("mask", action="store", help="mask file for grd files")
        parser.add_argument("target", action="store", help="root dir for source files")
        parser.add_argument("-t","--tempDir", dest="tempDir", action="store", help="root dir for temporary files")
        parser.add_argument("-i", "--include", dest="include", action="store", help="file for storing valid files list")
        parser.add_argument("-e", "--exclude", dest="exclude", action="store", help="file for storing excluesive files list")

    """ main route for processing """
    def run(self, args):
        srcRoot = args.source
        maskPath = args.mask
        targetRoot = args.target
        tempDir = args.tempDir
        inclusiveFilesPath = args.include
        exclusiveFilesPath = args.exclude

        targetPathRoot = os.path.dirname(targetRoot)
        if not os.path.exists(targetPathRoot):
            os.makedirs(targetPathRoot)

        self._logger.info("Starting: Batch process for converting grids to series.")

        self.setupProcessEnv(tempDir)
        self.batchProcess(srcRoot, maskPath, targetRoot, inclusiveFilesPath, exclusiveFilesPath)

        self._logger.info("Finished: Batch process for converting grids to series.")

    def batchProcess(self, srcPathRoot, maskPath,  targetPath, inclusiveFileListPath=None, exclusiveFilePath=None):
        # loading data and mask files
        self.loadBatchFileList(srcPathRoot, inclusiveFileListPath, exclusiveFilePath)
        maskRaster = self.loadMaskRaster(maskPath)

        dataRasters = self.loadDataFilesAsRasterArray(srcPathRoot, maskRaster)
        if len(dataRasters) < 1:
            print("No Raster Series and nothing is processed.")
            return

        # todo what you like with raster Array
        self.doCustomProcessWithRasters(dataRasters)

        # convert series format from rasters
        seriesArray = self.rasters2Series(dataRasters)

        # todo what you like with series Array
        self.doCustomProcessWithSeriesArray(seriesArray)

        self.saveSeries(seriesArray, targetPath)

        gridFilePath = os.path.join(self.tempDir, "indexgrd")
        self.saveIndexedGrid( seriesArray,dataRasters[0], gridFilePath)

    def setupProcessEnv(self, tempDir):
        arcpy.env.overwriteOutput = True
        # Set environment settings
        self.tempDir = tempDir
        if self.tempDir is None:
            self.tempDir = os.path.join(os.getcwd(),"temp")

        if not os.path.exists(self.tempDir):
            os.makedirs(self.tempDir)
        # env.workspace = tempDir

    """ Do custom processing whatever you want with raster array and return result in any format."""
    def doCustomProcessWithRasters(self,rasters):
        self._logger.info("Do custom processing whatever you want with raster array and return result in any format.")
        pass;

    """ Do custom processing whatever you want with the series.py data array and return result in any format."""
    def doCustomProcessWithSeriesArray(self, seriesArray):
        self._logger.info("Do custom processing whatever you want with the series array and return result in any format.")
        pass;


    """" Convert Raster Array into SeriesArray like a table without header, format: index, i, j, x, y, v1,v2,... """
    def rasters2Series(self, dataRasters):
        self._logger.info("Converting rasters into series ...")
        dataNpArray = self.rasters2NumPyArray(dataRasters)

        raster = dataRasters[0]
        extent = raster.extent
        cellWidth = raster.meanCellWidth
        cellHeight = raster.meanCellHeight
        noDataValue = raster.noDataValue
        row = raster.height
        col = raster.width

        index = 0

        i = 0
        j = 0
        seriesArray = []
        for i in range(row):
            y = extent.YMax - cellHeight * (i + 0.5)
            for j in range(col):
                if (dataNpArray[0, i, j] != noDataValue):
                    x = extent.XMin + cellWidth * (j + 0.5)
                    index += 1

                    series = dataNpArray[:, i, j]
                    seriesArray.append(SeriesWithLocation(index, i, j, x, y, series))

        self._logger.info("Done: converting rasters into series ...")
        return seriesArray

    def rasters2NumPyArray(self, rasters):
        dataArray = []
        for i in range(len(rasters)):
            dataArray.append(arcpy.RasterToNumPyArray(rasters[i]))
        data = np.array(dataArray)
        return data

    """Save series.py to text files in table format."""
    def saveSeries(self, seriesArray, targetPath):
        dir = os.path.dirname(targetPath)
        if not os.path.exists(dir):
            os.mkdir(dir)

        with open(targetPath, "w") as fts:
            for ii in range(len(seriesArray)):
                series = seriesArray[ii].toString
                fts.write(series)


    """Exclude the files in the list load from configue file for exclusive items"""
    def loadBatchFileList(self, srcPathRoot, inclusiveFilesPath=None, exclusiveFilesPath=None):
        self._taskList = []
        if inclusiveFilesPath is None:
            arcpy.env.workspace = srcPathRoot
            self._taskList = arcpy.ListRasters("*", "GRID")
            for rasterFile in self._taskList:
                 print("Loading %s" % rasterFile)
                # self._logger.info(rasterFile)
        else:
            with open(inclusiveFilesPath) as fbo:
                for line in fbo.readlines():
                 self._taskList.append(line.strip('\n'))

        self._taskExclusiveList = []
        if exclusiveFilesPath is None:
            return
        with open(exclusiveFilesPath) as feo:
            for line in feo.readlines():
                self._taskExclusiveList.append(line.strip('\n'))

    """Open and load the files in the list clipped with mask, return as Raster Array"""
    def loadDataFilesAsRasterArray(self, srcPathRoot, maskRaster):
        if not maskRaster is None:
            # Check out the ArcGIS Spatial Analyst extension license
            arcpy.CheckOutExtension("Spatial")

        rasters = []
        for item in self._taskList:
            if item not in self._taskExclusiveList:
                srcPath = os.path.join(srcPathRoot, item)
                if arcpy.Exists(srcPath):
                    raster = arcpy.sa.Raster(srcPath)
                    if not maskRaster is None:
                        raster = arcpy.sa.ExtractByMask(raster, maskRaster)
                    rasters.append(raster)
                else:
                    print("Raster %s doesn't exist! check it please." % item)
        return rasters

    def loadMaskRaster(self, maskPath):
        if not os.path.exists(maskPath):
            self._logger.error("Mask raster file is missing or incorrect! Correct it and run again.")
        maskRaster = arcpy.sa.Raster(maskPath)
        # self.printMask(maskArray)
        return maskRaster

    """" Create grid index by the series's index, x, y. """
    def saveIndexedGrid(self,seriesArray, refRaster, gridFilePath ):
        self._logger.info("Saving Index Grid ...")
        # gridArray = np.zeros((refRaster.height, refRaster.width), dtype=np.int64)
        gridArray = np.zeros((refRaster.height, refRaster.width),dtype=np.int)

        for ii in range(len(seriesArray)):
            s = seriesArray[ii]
            gridArray[s.i, s.j] = s.index

        # Convert array to a geodatabase raster
        gridRaster = arcpy.NumPyArrayToRaster(gridArray, refRaster.extent.lowerLeft, refRaster.meanCellWidth, refRaster.meanCellHeight, 0)
        gridRaster.save(gridFilePath)
        self._logger.info("Done: saving Index Grid ...")
        del gridRaster

    def printMask(self, maskRaster):
        maskArray = arcpy.RasterToNumPyArray(maskRaster)
        row, col = maskArray.shape
        print("row:%d  col%d" %(row, col))
        workspace = os.getcwd()
        txmaskfile = os.path.join(self.tempDir , "txmask.txt")
        print("write mask file in text %s", txmaskfile)
        with open(txmaskfile, "w") as fts:
            for i in range(row):
                strMask = u"{}\n".format(("%s" % maskArray[i]).strip("[]"))
                fts.write(strMask)

if __name__ == "__main__":
        # testing code
    tool = Grid2SeriesConverterTool()

    import argparse
    from logger import Logger
    parser = argparse.ArgumentParser(prog="python.exe grid2seriestool.py", description="Grid2SeriesConverterTool Usage Guide", prefix_chars="-+/")
    parser.add_argument("--version", action="version", version="%(prog)s 0.0.1")
    tool.defineArgumentParser(parser)

    logger = Logger("log/g2s.log")

    tool.attachLogger(logger)
    args = parser.parse_args()
    # print(args)
    tool.run(args)

else:
    print("loading grid2seriestool module")
