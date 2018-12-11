#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import system modules
import os
import sys
import arcpy
import re

def redefineSpatialReference(dataset):
    try:
        # arcpy.env.workspace = workspace
        # set local variables
        srcProj = os.path.join(os.path.split(os.path.realpath(__file__))[0], "6842.prj")
        in_dataset = dataset #"forest.shp"
        coord_sys= arcpy.SpatialReference(srcProj)
        # run the tool
        arcpy.DefineProjection_management(in_dataset, coord_sys)
        # print messages when the tool runs successfully
        print(arcpy.GetMessages(0))

    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))

    except Exception as ex:
        print(ex.args[0])

def albersOffset(dataset, offset_degs):
    try:
        # set local variables
        dsc = arcpy.Describe(dataset)

        # get the coordinate system by describing a feature class
        coord_sys = dsc.spatialReference
        # Impossible
        # coord_sys.centralMeridian = 105 #offset_degs
        crs = re.sub('PARAMETER\[\'central_meridian\'\,.+?]',
                         'PARAMETER\[\'central_meridian\',' + offset_degs +']',
                         coord_sys.exportToString())
        # print(crs)
        coord_sys.loadFromString(crs)
        
        # print(coord_sys, coord_sys.centralMeridian, offset_degs)

        # run the tool
        arcpy.DefineProjection_management(dataset, coord_sys)

        # print messages when the tool runs successfully
        print(arcpy.GetMessages(0))

    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
    except Exception as ex:
        print(ex.args[0])
        
def pyramidsAndStatistics(workspace):
    try:
        arcpy.BuildPyramidsandStatistics_management(workspace, "INCLUDE_SUBDIRECTORIES","BUILD_PYRAMIDS","CALCULATE_STATISTICS")
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
    except Exception as ex:
        print(ex.args[0])

def printUsage():
    print("Usage: ")
    print("python gee_post.py build <tif_dir> : \
                Build pyramids and statistics for images.")
    print("python gee_post.py sr-org-6974 <tif_dir> : \
                replace modis image' coordinate system(sr-org:6974) with sr-org:6842.")
    print("python gee_post.py albers <tif_dir> <offset_degrees> : \
                update modis image' Central_Meridian offset in Degrees under Albers projection system.")

    
if __name__ == "__main__":
    # set workspace environment
    if len(sys.argv) <= 2:
        printUsage()

    else:
        print(sys.argv)
        sub_cmd = sys.argv[1]
        workspace = os.path.realpath(sys.argv[2])
        arcpy.env.workspace = workspace
        if sub_cmd == "build":
            pyramidsAndStatistics(workspace)
        else:
            for file in os.listdir(workspace):
                path = os.path.join(workspace, file)
                if not os.path.isdir(path):
                    if os.path.splitext(path)[1] == '.tif':
                        if sub_cmd == "sr-org-6974":
                            redefineSpatialReference(path)
                        elif sub_cmd == "albers" and len(sys.argv) >3:
                            albersOffset(path, sys.argv[3])
                        else:
                            printUsage()
                            break;
