import os
import glob
import shutil
import datetime
import re
from random import randint


import arcpy
# from arcpy import env
# from arcpy.sa import *


# input: 46 files(GLASS11A01.V42.A{YYYY}***.h{HH}v{VV}.*.hdf)
# with same YYYY, HH and VV.
def calcYearlyValues(inputDir, product, h, v, year, resultDir, tempDir):
    outputFilePattern = "{0}.YEARLY.A{1}.h{2}v{3}{4}.tif"

    randNum = str(randint(0, 10000000))
    temp_tif1 = os.path.join(
        tempDir,
        outputFilePattern.format(
            productPrefix(product), year, h, v, "_" + randNum + "_p01"))
    temp_tif2 = os.path.join(
        tempDir,
        outputFilePattern.format(
            productPrefix(product), year, h, v, "_" + randNum + "_p02"))

    outputFile = outputFilePattern.format(
            productPrefix(product),
            year, h, v, "")
    outputPath = (os.path.join(resultDir, outputFile))

    files = glob.glob(os.path.join(inputDir, "*.hdf"))
    files.sort()

    count = len(files)
    if count < 23:
        print("error: only {} valid files found in {}".format(
            count,  inputDir))
        return
    if count >= 23 and count < 46:
        print("warning: {} valid files found in {}".format(
            count,  inputDir))
        # caculate even less than 46 files

    ignore_nodata = "DATA"
    # ignore_nodata = "NODATA"

    # tempRaster = arcpy.sa.Times(files[0], 8)
    # for i in range(1, count/2):
    #     f = files[i]
    #     # print(f)
    #     tempRaster = arcpy.sa.Plus(arcpy.sa.Times(f, 8), tempRaster)
    tempRaster = arcpy.sa.Times(
            arcpy.sa.CellStatistics(files[:count/2], "SUM", ignore_nodata),
            8)
    tempRaster.save(temp_tif1)

    # f = files[count/2]
    # tempRaster = arcpy.sa.Times(files[count/2], 8)
    # for i in range(count/2+1, count-1):
    #     f = files[i]
    #     # print(f)
    #     tempRaster = arcpy.sa.Plus(arcpy.sa.Times(f, 8), tempRaster)
    tempRaster = arcpy.sa.Times(
            arcpy.sa.CellStatistics(
                files[count/2: count-1],
                "SUM", ignore_nodata),
            8)

    f = files[count-1]
    m = re.search(r"\d{4}361", f)
    if m:
        daysInLastRaster = lastDays(year)
    else:
        daysInLastRaster = 8

    tempRaster = arcpy.sa.CellStatistics(
            [tempRaster, arcpy.sa.Times(f, daysInLastRaster)],
            "SUM", ignore_nodata)

    # tempRaster = arcpy.sa.Plus(
    #         arcpy.sa.Times(f, daysInLastRaster),
    #         tempRaster)
    tempRaster.save(temp_tif2)

    scale = scaleOfProduct(product)
    yearlyRaster = arcpy.sa.Times(
            arcpy.sa.CellStatistics(
                [temp_tif1, temp_tif2],
                "SUM", ignore_nodata),
            scale)
    # yearlyRaster = arcpy.sa.Times(arcpy.sa.Plus(temp_tif1, temp_tif2), scale)
    yearlyRaster.save(outputPath)

    try:
        del tempRaster
        del yearlyRaster
        os.remove(temp_tif1)
        os.remove(temp_tif2)
    except OSError as e:
        print("Error: %s" % (e.strerror))


def lastDays(year):
    d2 = datetime.datetime(year + 1, 1, 1)
    d1 = datetime.datetime(year, 1, 1)

    dif_days = (d2 - d1).days - 8 * 45
    return dif_days


def maximumByYear(inputDir, product, h, v, year, resultDir, tempDir):
    files = glob.glob(os.path.join(inputDir, "*.hdf"))
    files.sort()
    # print(files)

    count = len(files)
    if count < 23:
        print("error: only {} valid files found in {}".format(
            count,  inputDir))
        return
    if count < 46:
        print("warning: {} valid files found in {}".format(
            count,  inputDir))
        # caculate maximum even less than 46 files
        # return

    inputRasters = []
    for f in files:
        inputRasters.append(f)
    # inputRasters = [arcpy.Raster(f) for f in files]
    outputFilePattern = "{0}.MAX.A{1}.h{2}v{3}{4}.tif"

    outputFile = outputFilePattern.format(
            productPrefix(product),
            year, h, v, "")
    outputPath = (os.path.join(resultDir, outputFile))

    randNum = str(randint(0, 10000000))
    temp_tif1 = os.path.join(
            tempDir,
            outputFilePattern.format(
                productPrefix(product), year, h, v,  "_" + randNum + "_p01"))
    temp_tif2 = os.path.join(
            tempDir,
            outputFilePattern.format(
                productPrefix(product), year, h, v,  "_" + randNum + "_p02"))

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

    try:
        del temp
        del resCellStatistics
        os.remove(temp_tif1)
        os.remove(temp_tif2)
    except OSError as e:
        print("Error: %s" % (e.strerror))


# helper functions
def productPrefix(product):
    if product == "LAI":
        return "GLASS01E01.V50"
    elif product == "ET":
        return "GLASS11A01.V42"
    else:
        print("invad product")
        return ""


def scaleOfProduct(product):
    if product == "LAI":
        return 0.1
    elif product == "ET":
        return 0.0003527
    else:
        print("invad product", product)
        return 1


# assuming: inputRoot, outputRoot, temp_dir exist and valid
def batach_statistics(
        statisticsType,
        inputRoot,
        outputRoot,
        temp_dir,
        outputOrganizedByYearFirst):

    subDirs = glob.glob(inputRoot + "/h??v??/????/")
    subDirs.extend(glob.glob(inputRoot + "/????/h??v??/"))

    subDirs.sort()
    hvYearPattern = re.compile(r'h(\d+)v(\d+)[\\\/](\d+)')
    yearHvPattern = re.compile(r'(\d+)[\\\/]h(\d+)v(\d+)')

    for path in subDirs:
        # print(path)
        m = hvYearPattern.search(path)
        if m:
            # print(m.group(1), m.group(2), m.group(3))
            h = m.group(1)
            v = m.group(2)
            year = m.group(3)
            hvPath = "h{0}v{1}".format(h, v)
            inputDir = os.path.join(inputRoot, hvPath, year)
        else:
            m = yearHvPattern.search(path)
            if m:
                year = m.group(1)
                h = m.group(2)
                v = m.group(3)
                hvPath = "h{0}v{1}".format(h, v)
                inputDir = os.path.join(inputRoot, year, hvPath)
            else:
                continue

        if outputOrganizedByYearFirst:
            outputDir = os.path.join(outputRoot, year)
        else:
            outputDir = os.path.join(outputRoot, hvPath)
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)

        print("processing {0}: {1}, h:{2}, v:{3}, year:{4}...".format(
            product, statisticsType, h, v, year))
        print(hvPath, str(year), inputDir, outputDir)

        if statisticsType == "maxValue":
            maximumByYear(
                    inputDir,
                    product,
                    h, v,
                    int(year),
                    outputDir,
                    temp_dir)
        elif statisticsType == "yearlyValue":
            calcYearlyValues(
                    inputDir,
                    product,
                    h, v,
                    int(year),
                    outputDir,
                    temp_dir)


if __name__ == "__main__":
    # # Check out the ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")
    arcpy.env.overwriteOutput = True
    # process LAI or ET
    # http://www.glass.umd.edu/LAI/MODIS/1km/
    # http://www.glass.umd.edu/ET/MODIS/1km/

    # --------------------------------------------------------------
    # Input parameters:

    # product = "LAI"
    product = "ET"
    statisticsType = "yearlyValue"
    # statisticsType = "maxValue"

    root = "Z:/share/glass"

    inputRoot = os.path.join(root, product)
    outputRoot = os.path.join(root, "statistics", product, statisticsType)
    outputOrganizedByYearFirst = True
    temp_dir = os.path.join(root, "temp")

    # or
    # inputRoot = "Z:/share/glass/" + product + "/hv"
    # outputRoot ="Z:/share/glass/statistics/" + product + "/" + statisticsType
    # outputOrganizedByYearFirst = True
    # temp_dir = "Z:/share/glass/" + "temp"
    # -------------------------------------------------------------
    if not os.path.exists(inputRoot):
        print("Invalid data directory", inputRoot)

    if not os.path.exists(outputRoot):
        os.makedirs(outputRoot)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    batach_statistics(
            statisticsType,
            inputRoot,
            outputRoot,
            temp_dir,
            outputOrganizedByYearFirst)

    try:
        shutil.rmtree(temp_dir)
    except OSError as e:
        print("Error: %s : %s" % (temp_dir, e.strerror))
