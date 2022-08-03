import os
import arcpy


def gee_post(inputRaster, args, outputRaster):
    # Process: Define Projection
    print("define projection -> {0} ...".format(inputRaster))
    arcpy.DefineProjection_management(inputRaster, args["projection"])

    # Process: Build Pyramids And Statistics
    print("build pyramids and statistics -> {0} ...".format(inputRaster))
    arcpy.BuildPyramidsandStatistics_management(
            inputRaster,
            "INCLUDE_SUBDIRECTORIES",
            "BUILD_PYRAMIDS",
            "CALCULATE_STATISTICS",
            "NONE",
            "",
            "NONE",
            "1",
            "1",
            "",
            "-1",
            "NONE",
            "NEAREST",
            "DEFAULT",
            "75",
            "SKIP_EXISTING")


def clip(inputRaster, args, outputRaster):
    print("clipping {0}  -->  {1}".format(inputRaster, outputRaster))
    arcpy.Clip_management(
            inputRaster,
            args.extent,
            outputRaster,
            args['clipShpPath'],
            args['nodata'],
            "NONE",
            "NO_MAINTAIN_EXTENT")


def batch_tools(src, cmd, args, dest):
    if not dest and os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    files = os.listdir(src_dir)
    for f in files:
        if f.endswith(".tif"):
            inputRaster = os.path.join(src_dir, f)
            outputRaster = os.path.join(dest_dir, f)
            cmd(inputRaster, args, outputRaster)


if __name__ == "__main__":
    # config tools
    cmds = {
            "clip": clip,
            "gee_post": gee_post
            }

    # clip task
    # op = "clip"
    # # relative path or absolute path
    # src_dir = "./CSR"
    # dest_dir = "./CSR_RES"
    # args = {
    #         "extent": "96.139801942 37.72004487 104.128480098 43.329166667",
    #         "clipShpPath": "./beijing.shp",
    #         "nodata": "-9.999900e+004"
    #         }
    # batch_tools(src_dir, cmds[op], args,  dest_dir)

    op = "gee_post"
    # for linux
    # src_dir = "/Users/hurricane/Downloads/PML"
    # src_dir = "/Users/hurricane/Downloads/PML"
    # for windows
    src_dir = "C:/ignrr/data/PML_V2/PML_V2_Anul_HH_2021"
    dest_dir = ""

    # todo: need better way to define projection
    # proj_param = "PROJCS[\'WGS_1984_Albers\',\
    #         GEOGCS[\'GCS_WGS_1984\',\
    #         DATUM[\'D_WGS_1984\',SPHEROID[\'WGS_1984\',6378137.0,298.257223563]],\
    #         PRIMEM[\'Greenwich\',0.0],UNIT[\'Degree\',0.0174532925199433]],\
    #         PROJECTION[\'Albers\'],\
    #         PARAMETER[\'False_Easting\',0.0],\
    #         PARAMETER[\'False_Northing\',0.0],\
    #         PARAMETER[\'Central_Meridian\',110.0],\
    #         PARAMETER[\'Standard_Parallel_1\',25.0],\
    #         PARAMETER[\'Standard_Parallel_2\',47.0],\
    #         PARAMETER[\'Latitude_Of_Origin\',12.0],\
    #         UNIT[\'Meter\',1.0]]"

    proj_param = "PROJCS[\'WGS_1984_Albers\',\
            GEOGCS[\'GCS_WGS_1984\',\
            DATUM[\'D_WGS_1984\',SPHEROID[\'WGS_1984\',6378137.0,298.257223563]],\
            PRIMEM[\'Greenwich\',0.0],UNIT[\'Degree\',0.0174532925199433]],\
            PROJECTION[\'Albers\'],\
            PARAMETER[\'False_Easting\',4000000.0],\
            PARAMETER[\'False_Northing\',0.0],\
            PARAMETER[\'Central_Meridian\',105.0],\
            PARAMETER[\'Standard_Parallel_1\',25.0],\
            PARAMETER[\'Standard_Parallel_2\',47.0],\
            PARAMETER[\'Latitude_Of_Origin\',0.0],\
            UNIT[\'Meter\',1.0]]"
    proj_param = proj_param.replace(" ", "")
    # print(proj_param)
    args = {
            "projection": proj_param
            }
    batch_tools(src_dir, cmds[op], args,  dest_dir)
