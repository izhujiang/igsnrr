"""
landsat images process module
"""
# -*- coding: utf-8 -*-
import os
import re
import arcpy


def BatchExtractValuesToPoints(Input_Landsat_dir, gdb, src_featureClass, outputTable_dir):
    PATTERN = re.compile(r'^[0-9a-zA-Z]*_[0-9a-zA-Z]*_(\d*)_(\d*)\w*\.tif$')
    YEARS_DIR = os.listdir(Input_Landsat_dir)
    for year_dir in YEARS_DIR:
        year_path = os.path.join(Input_Landsat_dir, year_dir)
        file_dict = {}
        if os.path.isdir(year_path):
            print("processing " + Input_Landsat_dir + ": year " + year_dir)
            files = os.listdir(year_path)
            for fname in files:
                fpath = os.path.join(year_path, fname)
                if os.path.isfile(fpath) and fpath.endswith(".tif"):
                    mo = PATTERN.match(fname)
                    ymd = mo.group(2)
                    if not ymd in file_dict:
                        file_dict[ymd] = []
                    file_dict[ymd].append(fname)
                    # print(mo.group(1), mo.group(2))
            keys = sorted(file_dict.keys())
            inRasterList = []
            for k in keys:
                f_list = sorted(file_dict[k])
                for f in f_list:
                    inRasterList.append([f,  k])
            # print(inRasterList)
            
            # Local variables:
            
            Zjt_org = gdb + "\\" + src_featureClass
            featureClasses =  src_featureClass + "_" + str(year_dir)
            inPointFeatures = gdb +  "\\" + featureClasses
            
            # Process: Copy
            arcpy.Copy_management(Zjt_org, inPointFeatures, "FeatureClass")

            # Execute ExtractValuesToPoints
            arcpy.env.workspace = year_path
            arcpy.sa.ExtractMultiValuesToPoints(inPointFeatures, inRasterList, "NONE")


            # TableToDBASE_conversion
            #  arcpy.TableToDBASE_conversion( inPointFeatures, output_dir)
            
            # Local variables:
            # Zjt_1995 = "C:\\ignrr\\data\\LT05\\Zjt.gdb\\Zjt_1995"
            # print("outputTableDir:" + outputTable_dir)
            zjt_xls = os.path.join(outputTable_dir, featureClasses + ".xls")
            # print(zjt_xls)
            # Process: Table To Excel
            arcpy.TableToExcel_conversion(inPointFeatures, zjt_xls, "ALIAS", "CODE")


# main programme
# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")
# GDB, where featureClasses are stored. 
zjt_gdb = "C:\\ignrr\\data\\LT05\\Zjt.gdb"
arcpy.env.workspace = zjt_gdb
outputTable_dir = "C:\\ignrr\\data\\LT05\\tables" 

if not os.path.exists(outputTable_dir):
    os.makedirs(outputTable_dir)

zjt_featureClass = "Zjt"
landsat_dir = "C:\\ignrr\\data\\LT05\\ndvi" 

BatchExtractValuesToPoints(landsat_dir, zjt_gdb, zjt_featureClass, outputTable_dir)

landsat_dir = "C:\\ignrr\\data\\LT05\\qa"
zjt_featureClass = "Zjt_QA"
BatchExtractValuesToPoints(landsat_dir, zjt_gdb, zjt_featureClass, outputTable_dir)