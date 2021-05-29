import os
import glob
import shutil
import datetime

# netcdf4 needs to be installed in your environment for this to work
# import numpy as np

import arcpy
# from arcpy import env
# from arcpy.sa import *


def calcYearlyValues(rootDir, product, h, v, year, resultDir):
    pattern = "/*.A{YYYY}*.h{HH}v{VV}.*.hdf".format(YYYY=year, HH=h, VV=v)
    curRootDir = os.path.join(rootDir, product, str(year))

    outputFilePattern = "{0}.YEARLY.A{1}.h{2}v{3}{4}.tif"

    temp_tif1 = os.path.join(
            resultDir,
            "temp",
            outputFilePattern.format(
                productPrefix(product), year, h, v, "_p01"))
    temp_tif2 = os.path.join(
                resultDir,
                "temp",
                outputFilePattern.format(
                    productPrefix(product), year, h, v, "_p02"))
    outputFile = outputFilePattern.format(
            productPrefix(product),
            year, h, v, "")
    outputPath = (os.path.join(resultDir, outputFile))

    files = []
    for root, dirnames, filenames in os.walk(curRootDir):
        files.extend(glob.glob(root + pattern))

    files.sort()

    count = len(files)
    if count != 46:
        print("error: only {} valid files found in {}".format(
            count,  curRootDir))
        return

    tempRaster = arcpy.sa.Times(files[0], 8)

    for i in range(1, count/2):
        f = files[i]
        print(f)
        tempRaster = arcpy.sa.Plus(arcpy.sa.Times(f, 8), tempRaster)
    tempRaster.save(temp_tif1)

    f = files[count/2]
    print(f)
    tempRaster = arcpy.sa.Times(files[count/2], 8)
    for i in range(count/2+1, count-1):
        f = files[i]
        print(f)
        tempRaster = arcpy.sa.Plus(arcpy.sa.Times(f, 8), tempRaster)
    tempRaster = arcpy.sa.Plus(
            arcpy.sa.Times(files[count-1], lastDays(year)),
            tempRaster)
    tempRaster.save(temp_tif2)

    yearlyRaster = arcpy.sa.Plus(temp_tif1, temp_tif2)
    yearlyRaster.save(outputPath)


def lastDays(year):
    d2 = datetime.datetime(year + 1, 1, 1)
    d1 = datetime.datetime(year, 1, 1)

    dif_days = (d2 - d1).days - 8 * 45
    return dif_days


def maximumByYear(rootDir, product, h, v, year, resultDir):
    pattern = "/*.A{YYYY}*.h{HH}v{VV}.*.hdf".format(YYYY=year, HH=h, VV=v)
    curRootDir = os.path.join(rootDir, product, str(year))

    files = []
    for root, dirnames, filenames in os.walk(curRootDir):
        # print(root + pattern)
        files.extend(glob.glob(root + pattern))

    files.sort()

    count = len(files)
    if count <= 0:
        print("error: {} valid files found in {}".format(
            count,  curRootDir))
        return

    inputRasters = []
    for f in files:
        print(f)
        inputRasters.append(f)
    # inputRasters = [arcpy.Raster(f) for f in files]
    outputFilePattern = "{0}.MAX.A{1}.h{2}v{3}{4}.tif"

    outputFile = outputFilePattern.format(
            productPrefix(product),
            year, h, v, "")
    outputPath = (os.path.join(resultDir, outputFile))

    temp_tif1 = os.path.join(
            resultDir,
            "temp",
            outputFilePattern.format(
                productPrefix(product), year, h, v, "_p01"))
    temp_tif2 = os.path.join(
            resultDir,
            "temp",
            outputFilePattern.format(
                productPrefix(product), year, h, v, "_p02"))

    # # Execute CellStatistics
    # outCellStatistics = CellStatistics([inRaster01, inRaster02, inRaster03],
    # "RANGE", "NODATA")
    half = len(files)/2
    temp = arcpy.sa.CellStatistics(inputRasters[:half], "MAXIMUM", "DATA")
    temp.save(temp_tif1)

    temp = arcpy.sa.CellStatistics(inputRasters[half:], "MAXIMUM", "DATA")
    temp.save(temp_tif2)

    resCellStatistics = arcpy.sa.CellStatistics(
            [temp_tif1, temp_tif2], "MAXIMUM", "DATA")
    resCellStatistics.save(outputPath)


# helper functions
def productPrefix(product):
    if product == "LAI":
        return "GLASS01E01.V50"
    elif product == "ET":
        return "GLASS11A01.V42"
    else:
        print("invad product")
        return ""


if __name__ == "__main__":

    # # Check out the ArcGIS Spatial Analyst extension license
    # arcpy.CheckOutExtension("Spatial")

    # process LAI or ET
    # http://www.glass.umd.edu/LAI/MODIS/1km/
    # http://www.glass.umd.edu/ET/MODIS/1km/

    # rootDir = "/Users/hurricane/share/glass"
    rootDir = "Z:\\share\\glass"

    product = "LAI"
    staticsType = "max"

    # product = "ET"
    # staticsType = "yearly"

    scenes = [
            ("25", "04"),
            # ("26", "04")
            ]
    resultDir = os.path.join(rootDir, staticsType, product)
    temp_dir = os.path.join(resultDir, "temp")

    if not os.path.exists(
            os.path.join(rootDir, product)):
        print("Invalid data directory", os.path.join(rootDir, product))

    if not os.path.exists(resultDir):
        os.makedirs(resultDir)

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    for year in range(2000, 2019):
        for hv in scenes:
            h, v = hv
            print("processing {} {} h{} v{} year {}...".format(
                product, staticsType, h, v, year))
            if staticsType == "max":
                maximumByYear(
                        rootDir,
                        product,
                        h, v,
                        year, resultDir)
            elif staticsType == "yearly":
                calcYearlyValues(
                        rootDir,
                        product,
                        h, v,
                        year,
                        resultDir)

    try:
        shutil.rmtree(temp_dir)
    except OSError as e:
        print("Error: %s : %s" % (temp_dir, e.strerror))
