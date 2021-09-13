import os
import re
import arcpy


if __name__ == "__main__":
    # # Check out the ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")
    arcpy.env.overwriteOutput = True
    # --------------------------------------------------------------
    # Input parameters:
    # root = "/Users/hurricane/share/glass/"
    root = "Z:/share/glass/"
    inputDir = root + "statistics/LAI/maxValue"
    outputDir = root + "statistics/LAI/maxValueAv"

    # -------------------------------------------------------------
    if not os.path.exists(inputDir):
        print("Invalid data directory", inputDir)
        exit(1)

    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    filePattern = re.compile(r'A(\d+)\.(h\d{2}v\d{2}).tif$')
    fileDict = {}
    for dirpath, dirs, files in os.walk(inputDir):
        for filename in files:
            ifname = os.path.join(dirpath, filename)
            m = filePattern.search(filename)
            if m:
                year = m.group(1)
                hv = m.group(2)
                if hv not in fileDict:
                    fileDict[hv] = []

                fileDict[hv].append(ifname)

    for hv, ifnames in fileDict.items():
        print("{0}: ".format(hv))
        ofname = os.path.join(
                outputDir,
                "GLASS01E01.V50.MAX.AV.{0}.tif".format(hv))
        print("caculating {0} --> {1} ...".format(hv, ofname))
        ifnames.sort()
        for ifname in ifnames:
            print(ifname)

        resCellStatistics = arcpy.sa.CellStatistics(
            ifnames, "MEAN", "DATA")
        resCellStatistics.save(ofname)
