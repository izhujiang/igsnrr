import os
import arcpy


if __name__ == "__main__":
    # --------------------------------------------------------------
    # Input parameters:

    # product = "LAI"
    product = "ET"

    root = "Z:/share/glass/"
    #  root = "/Users/hurricane/share/glass/"
    inputDir = root + "statistics/ET/"
    outputDir = root + "proj/ET/"
    prjFile = root + "WGS_1984_Albers.prj"

    # -------------------------------------------------------------

    arcpy.env.overwriteOutput = True
    if not os.path.exists(inputDir):
        print("Invalid data directory", inputDir)
        exit(1)

    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    spatialRef = arcpy.SpatialReference(prjFile)

    for dirpath, dirs, files in os.walk(inputDir):
        for filename in files:
            ifname = os.path.join(dirpath, filename)
            ofname = ifname.replace(inputDir, outputDir)
            if ifname.endswith('.tif'):
                targetDir = dirpath.replace(inputDir, outputDir)
                if not os.path.exists(targetDir):
                    os.makedirs(targetDir)

                print("transforming {0} --> {1} ...".format(ifname, ofname))
                ofname = ifname.replace(inputDir, outputDir)
                arcpy.ProjectRaster_management(
                        ifname,
                        ofname,
                        spatialRef,
                        "BILINEAR",
                        "", "", "#", "#")
