import os
import arcpy


def DefineProjectionRaster(in_dataset, coord_sys):
    try:
        # run the tool
        arcpy.DefineProjection_management(in_dataset, coord_sys)

        # print messages when the tool runs successfully
        print(arcpy.GetMessages(0))

    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))

    except Exception as ex:
        print(ex.args[0])


# define or re-define projection for all the files in the workspace/directory
def DefineProjectionDataset(workspace, prjFile):

    rasters = []
    walk = arcpy.da.Walk(workspace, topdown=True,
                         datatype="RasterDataset", type=['GRID', 'IMG', 'TIF'])

    for dirpath, dirnames, filenames in walk:
        # Disregard any folder named 'back_up' in creating list of rasters
        if "back_up" in dirnames:
            dirnames.remove('back_up')
        for filename in filenames:
            rasters.append(os.path.join(dirpath, filename))

    # print("rasters", rasters)

    # Set the current workspace
    # arcpy.env.workspace = dataPath
    # Get and print a list of GRIDs from the workspace
    # rasters = arcpy.ListRasters("*", "GRID")

    # get the coordinate system by describing a feature class
    dsc = arcpy.Describe(prjFile)
    coord_sys = dsc.spatialReference
    for raster in rasters:
        print("defining projection for{0}".format(raster))
        DefineProjectionRaster(raster, coord_sys)


if __name__ == "__main__":
    # data source path, using "/" or "\\"
    dataWorkspace = "Z:/share/uv/data"
    prjPath = "Z:/share/uv/bound_simulation.prj"
    DefineProjectionDataset(dataWorkspace, prjPath)
