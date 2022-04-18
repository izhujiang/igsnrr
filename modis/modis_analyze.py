#!/usr/bin/env python3
# Import system modules
import os
import re

import time
import arcpy
from arcpy import env
from arcpy.sa import *


def modis_statistics(inputWorkspace, outputDir, stat_method):
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    for item in os.listdir(inputWorkspace):
        curDir = os.path.join(inputWorkspace, item)
        if os.path.isdir(curDir) and re.match("\d{4}", item):
            eleArr = ["NDVI", "EVI"]
            for ele in eleArr:
                prefix = "MOD13Q1.061__250m_16_days_{0}".format(ele)
                filterFunc = makeFilterFunc(prefix + "\w+\d{7}\w+\.tif$")
                outputPath = os.path.join(
                    outputDir, "{0}_{1}_median.tif".format(prefix, item))
                print(
                    "cell_statistics:  {0}  {1}  -->  {2}".format(item, prefix, outputPath))
                cell_statistics(curDir, filterFunc, stat_method, outputPath)


def makeFilterFunc(pattern):
    def filterFunc(item):
        if re.match(pattern, item):
            m = re.search("(\d{7})", item)
            doy = int(m.group(0)[4:])
            if doy >= 97 and doy < 305:
                return True
        return False

    return filterFunc


def cell_statistics(inputDir, filterFunc, stat_method, outputPath):
    env.workspace = inputDir
    rasters = os.listdir(inputDir)
    inputRasters = filter(filterFunc, rasters)

    validRasters = []
    for r in inputRasters:
        validRasters.append(r)
    if validRasters is None or len(validRasters) == 0:
        return

    validRasters.sort()
    print("analyzing and saving", validRasters, outputPath)
    # print(validRasters)
    outRaster = CellStatistics(validRasters, stat_method, "DATA")
    outRaster.save(outputPath)


def SmoothRaster(img1, img2, img3, resImg, tempdir, randScale="10"):
    # Local variables:
    t = time.time()
    internal_iter = int(t * 1000)
    tmps = []
    for i in range(10):
        tmps.append(os.path.join(
            tempdir, "tmp_{0}.tif".format(internal_iter + i)))

    constRaster2 = "2"
    totalWeightsRaster = "4"
    img2_times2 = tmps[0]
    img2_img1_plus = tmps[1]
    img_sum = tmps[2]
    img_av = tmps[3]
    img_av_int = tmps[4]

    const_rand = "0.5"
    const_rand_scale = randScale
    img_rand = tmps[5]
    img_rand2 = tmps[6]
    img_rand3 = tmps[7]
    img_rand_int = tmps[8]
    img_av_int_rand = tmps[9]

    print("processing: {0}  -> {1}".format(img2, resImg))
    # (img1 + img2 * 2 + img3) / 4
    arcpy.gp.Times_sa(img2, constRaster2, img2_times2)
    arcpy.gp.Plus_sa(img1, img2_times2, img2_img1_plus)
    arcpy.gp.Plus_sa(img2_img1_plus, img3, img_sum)
    arcpy.gp.Divide_sa(img_sum, totalWeightsRaster, img_av)
    arcpy.gp.Int_sa(img_av, img_av_int)

    # (randRaster() - 0.5) * scale
    arcpy.gp.CreateRandomRaster_sa(img_rand, "", img2, img2)
    arcpy.gp.Minus_sa(img_rand, const_rand, img_rand2)
    arcpy.gp.Times_sa(img_rand2, const_rand_scale, img_rand3)
    arcpy.gp.Int_sa(img_rand3, img_rand_int)

    # img_av + img_rand
    arcpy.gp.Plus_sa(img_av_int, img_rand_int, img_av_int_rand)
    # if img_av_int_rand is null, use img2
    # print("debug...", img_av_int_rand, img2, resImg)
    # arcpy.gp.Con_sa(img_con, img_t, resImg, img_f, "")
    arcpy.gp.Con_sa(IsNull(Raster(img_av_int_rand)),
                    img2, resImg, img_av_int_rand, "")


def SmoothRasterArray(inputDir, outputDir, tempDir, ele, randScale="10", loopCount=1):
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    if not os.path.exists(tempDir):
        os.makedirs(tempDir)

    t = time.time()
    tm = int(t * 1000)

    tmpOutputDir0 = os.path.join(tempDir, str(tm))
    # print("tmpOutputDir0", tmpOutputDir0)
    if not os.path.exists(tmpOutputDir0):
        os.makedirs(tmpOutputDir0)
    env.workspace = tmpOutputDir0

    prefix = "MOD13Q1.061__250m_16_days_{0}".format(ele)
    fp = prefix + "\w+\d{7}\w+\.tif$"
    reg = re.compile(fp)
    # files = os.listdir(inputDir)
    # files = [f for f in files if f.endswith(".tif")]
    files = os.listdir(inputDir)
    files = [f for f in files if reg.match(f)]
    if len(files) <= 2:
        return

    files.sort()
    print("processing ...")
    for i in range(len(files)):
        print(os.path.join(inputDir, files[i]))

    inRasters = [os.path.join(inputDir, fo) for fo in files]

    count = len(inRasters)
    outputDirs = []
    for i in range(loopCount - 1):
        tmpOutputDir = os.path.join(tempDir, str(tm + i + 1))
        if not os.path.exists(tmpOutputDir):
            os.makedirs(tmpOutputDir)
        outputDirs.append(tmpOutputDir)

    outputDirs.append(outputDir)
    # print("outputDirs:", outputDirs)

    for k in range(loopCount):
        outRasters = []
        outRasters.append(inRasters[0])
        for i in range(1, count - 1):
            img1 = inRasters[i - 1]
            img2 = inRasters[i]
            img3 = inRasters[i + 1]
            resRaster = os.path.join(outputDirs[k], os.path.basename(img2))
            # print("resRaster: ", resRaster, "k=", k)
            SmoothRaster(img1, img2, img3, resRaster, tmpOutputDir0, randScale)

            outRasters.append(resRaster)

        outRasters.append(inRasters[count - 1])
        inRasters = outRasters

    # copy the two-end rasters
    img1 = inRasters[0]
    resRaster = os.path.join(outputDir, os.path.basename(img1))
    arcpy.gp.Int_sa(img1, resRaster)
    img3 = inRasters[count - 1]
    resRaster = os.path.join(outputDir, os.path.basename(img3))
    arcpy.gp.Int_sa(img3, resRaster)

    # remove temp dir
    arcpy.Delete_management(tmpOutputDir0, "Folder")
    for k in range(loopCount - 1):
        arcpy.Delete_management(outputDirs[k], "Folder")


def TestSmoothRasterArray():
    inputDir = "Z:/share/modis2/MOD13Q1.061/2020"
    outputDir = "Z:/share/modis3/MOD13Q1.061/2020"
    tempDir = "Z:/share/modis/temp"
    randScale = "20"  # the standard deviation of the standard deviation
    loopCount = 2
    ele = "NDVI"
    SmoothRasterArray(inputDir, outputDir, tempDir, ele, randScale, loopCount)


def SmoothRastersByWorkspace(inputWorkspace, outputWorkspace, tempDir, randScale="20", loopCount=1):
    eles = ["NDVI", "EVI"]
    for ele in eles:
        subItems = os.listdir(inputWorkspace)
        for item in subItems:
            input = os.path.join(inputWorkspace, item)
            if os.path.isdir(input):
                output = os.path.join(outputWorkspace, item)
                SmoothRasterArray(input, output, tempDir,
                                  ele, randScale, loopCount)


def CopyAndFilterRaster(inputWorkspace, outputWorkspace):
    for d in os.listdir(inputWorkspace):
        if os.path.isdir(os.path.join(inputWorkspace, d)):
            inputDir = os.path.join(inputWorkspace, d)
            outputDir = os.path.join(outputWorkspace, d)
            if not os.path.exists(outputDir):
                os.makedirs(outputDir)

            eleArr = ["NDVI", "EVI"]
            for ele in eleArr:
                prefix = "MOD13Q1.061__250m_16_days_{0}".format(ele)
                fp = prefix + "\w+\d{7}\w+\.tif$"
                reg = re.compile(fp)

                files = os.listdir(inputDir)
                files = [f for f in files if reg.match(f)]
                files.sort()
                for fname in files:
                    fInput = os.path.join(inputDir, fname)
                    fOutput = os.path.join(outputDir, fname)

                    m = re.search("(\d{7})", fname)
                    doy = int(m.group(0)[4:])
                    if doy >= 97 and doy < 305:
                        print("{0}  -->  {1}".format(fInput, fOutput))
                        arcpy.CopyRaster_management(
                            fInput, fOutput, "", "", "", "NONE", "NONE", "", "NONE", "NONE", "", "NONE")


if __name__ == "__main__":
    arcpy.CheckOutExtension("Spatial")

    inputWorkspace = "Z:/share/modis/MOD13Q1.061"
    outputWorkspace = "Z:/share/modis2/MOD13Q1.061"
    # inputWorkspace = "/Users/hurricane/share/modis/MOD13Q1.061"

    if not os.path.exists(outputWorkspace):
        os.makedirs(outputWorkspace)

    # step 1: filter valid files
    CopyAndFilterRaster(inputWorkspace, outputWorkspace)

    # step 2 (optional): smooth rasters
    inputWorkspace = outputWorkspace
    outputWorkspace = "Z:/share/modis3/MOD13Q1.061"
    tempDir = "Z:/share/modis/temp"
    randScale = "20"  # the standard deviation of the standard deviation
    loopCount = 1

    SmoothRastersByWorkspace(
        inputWorkspace, outputWorkspace, tempDir,  randScale, loopCount)

    # step 3: statistics("MEDIAN") rasters
    inputWorkspace = outputWorkspace
    outputWorkspace = "Z:/share/modis4/MOD13Q1.061"
    stat_method = "MEDIAN"
    modis_statistics(inputWorkspace, outputWorkspace, stat_method)