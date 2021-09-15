import os
import glob
import shutil
import datetime
import re
from random import randint


import arcpy
# from arcpy import env
# from arcpy.sa import *

# calculate of the summary 
# input: 46 files(GLASS11A01.V42.A{YYYY}***.h{HH}v{VV}.*.hdf)
# with same YYYY, HH and VV.
def calcYearlyValues(files, product, h, v, year, resultDir, tempDir):
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
    
    files.sort()
    count = len(files)
    if count < 23:
        print("error: only {0} valid files found in year:{1} h:{2} v:{3}".format(
            count,  year, h, v))
        return
    if count >= 23 and count < 46:
        print("warning: {0} valid files found in year:{1} h:{2} v:{3}".format(
            count,  year, h, v))
        # caculate even less than 46 files

    inputRasters = []
    if product == "LAI":
        filterRaster = filterLAIRaster
    elif product == "ET":
        filterRaster = filterETRaster
    else:
        filterRaster = defaultFilter

    for f in files:
        r = filterRaster(f)
        inputRasters.append(r)

    ignore_nodata = "DATA"
    # ignore_nodata = "NODATA"

    tempRaster = arcpy.sa.Times(
            arcpy.sa.CellStatistics(inputRasters[:count/2], "SUM", ignore_nodata),
            8)
    tempRaster.save(temp_tif1)

    tempRaster = arcpy.sa.Times(
            arcpy.sa.CellStatistics(
                inputRasters[count/2: count-1],
                "SUM", ignore_nodata),
            8)

    f = files[count-1]
    m = re.search(r"\d{4}361", f)
    if m:
        daysInLastRaster = lastDays(year)
    else:
        daysInLastRaster = 8
    lastRaster = inputRasters[count-1]

    tempRaster = arcpy.sa.CellStatistics(
            [tempRaster, arcpy.sa.Times(lastRaster, daysInLastRaster)],
            "SUM", ignore_nodata)

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

# maximiun 
# input: 46 files(GLASS11A01.V42.A{YYYY}***.h{HH}v{VV}.*.hdf)
# with same YYYY, HH and VV.
def maximumByYear(files, product, h, v, year, resultDir, tempDir):
    # file pattern "*A{year}*.h{h}v{v}*.hdf" for glass file likes GLASS01E01.V50.A2002001.h25v04.2020323.hdf
    filepattern = "*A{year}*.h{h}v{v}*.hdf".format(year=year, h=h, v=v)
    files.sort()

    count = len(files)
    if count < 23:
        print("error: only {0} valid files found in year:{1} h:{2} v:{3}".format(
            count,  year, h, v))
        return
    if count < 46:
        print("warning: {0} valid files found in year:{1} h:{2} v:{3}".format(
            count,  year, h, v))
        # caculate maximum even less than 46 files
        # return

    inputRasters = []
    if product == "LAI":
        filterRaster = filterLAIRaster
    elif product == "ET":
        filterRaster = filterETRaster
    else:
        filterRaster = defaultFilter

    for f in files:
        r = filterRaster(f)
        inputRasters.append(r)
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
    ignore_nodata = "DATA"
    # ignore_nodata = "NODATA"

    half = len(files)/2
    temp = arcpy.sa.CellStatistics(inputRasters[:half], "MAXIMUM", ignore_nodata)
    temp.save(temp_tif1)

    temp = arcpy.sa.CellStatistics(inputRasters[half:], "MAXIMUM", ignore_nodata)
    temp.save(temp_tif2)

    # resCellStatistics = arcpy.sa.CellStatistics(
    #        [temp_tif1, temp_tif2], "MAXIMUM", "DATA")

    scale = scaleOfProduct(product)
    resCellStatistics = arcpy.sa.Times(
            arcpy.sa.CellStatistics(
            [temp_tif1, temp_tif2], "MAXIMUM", ignore_nodata),
            scale)

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

# filter LAI raster
def filterLAIRaster(raster):
    inRaster = arcpy.Raster(raster)
    inTrueRaster = inRaster
    # inFalseConstant = 0

    # Execute Con
    outRaster = arcpy.sa.Con(inRaster<100, inTrueRaster ) 
    return outRaster

# todo: some filters with ET raster
def filterETRaster(raster):
    outRaster =arcpy.Raster(raster)
    return outRaster

# do nothing
def defaultFilter(raster):
    outRaster =arcpy.Raster(raster)
    return outRaster

# assuming: inputRoot, outputRoot, temp_dir exist and valid
def batach_statistics(
        statisticsType,
        inputRoot,
        outputRoot,
        temp_dir,
        outputOrganizedByYearFirst):
    # GLASS01E01.V50.A2002001.h25v04.2020323.hdf
    filePattern = re.compile(".*A(\d{4}).*\.h(\d{2})v(\d{2}).*\.hdf$")

    # group files by (year, h, v)
    fgroup = {}
    for curRoot, _, files in os.walk(inputRoot):
        for f in files:
            m = filePattern.search(f)
            if m:
                year = m.group(1)
                h = m.group(2)
                v = m.group(3)
                k = "A{0}h{1}v{2}".format(year, h, v)
                if not k in fgroup:
                    fgroup[k] = []
                fgroup[k].append(os.path.join(curRoot, f))
    
    for k, files in fgroup.items():
        year = k[1:5]
        h = k[6:8]
        v = k[9:11]
        
        if outputOrganizedByYearFirst:
            outputDir = os.path.join(outputRoot, year)
        else:
            hvPath = "h{0}v{1}".format(h, v)
            outputDir = os.path.join(outputRoot, hvPath)
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
 
        print("processing {0}: {1}, h:{2}, v:{3}, year:{4}...".format(
            product, statisticsType, h, v, year))
 
        if statisticsType == "maxValue":
            maximumByYear(
                    files,
                    product,
                    h, v,
                    int(year),
                    outputDir,
                    temp_dir)
        elif statisticsType == "yearlyValue":
            calcYearlyValues(
                    files,
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

    product = "LAI"
    # product = "ET"
    # statisticsType = "yearlyValue"
    statisticsType = "maxValue"

    root = "Z:/share/glass"

    # input and output directories
    inputRoot = os.path.join(root, product)
    outputRoot = os.path.join(root, "statistics", product, statisticsType)
    outputOrganizedByYearFirst = True
    temp_dir = os.path.join(root, "temp")
    # or
    # inputRoot = "Z:/share/glass/" + product 
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
