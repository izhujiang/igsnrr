#!/usr/bin/env python3
import os
import arcpy

statistics_methods = {
    "Maximum": arcpy.ia.Max,
    "Median": arcpy.ia.Median,
    # Min: arcpy.ia.Min,
    # Mean: arcpy.ia.Mean,
    # Sum: arcpy.ia.Sum,
    #Std: arcpy.ia.StandardDeviation,
    # Var: arcpy.ia.Variance,
    # Range: arcpy.ia.Range,
    # Count: arcpy.ia.Count,
    # Min_Max: arcpy.ia.MinMax,
    # Min_Mean: arcpy.ia.MinMean,
    # Min_Std: arcpy.ia.MinStandardDeviation,
}

def is_valid_tiff(path):
    if path.lower().endswith(".tif"):
        return True

def print_info(path):
    print(f"  Found TIFF: {path}")

def calc_ndvi(src_path, dest_path):
    if src_path.lower().endswith(".tif"):
        print(f"Processing ndvi: {src_path}")
        # Define output path
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Create Raster object
        in_raster = src_path
        # raster = arcpy.Raster(in_raster)

        # Band 3 = Red, Band 4 = NIR (1-based indexing in ArcPy)
        red = arcpy.Raster(f"{in_raster}/Band_3")
        nir = arcpy.Raster(f"{in_raster}/Band_4")

        # Calculate NDVI
        ndvi = (nir - red) / (nir + red)

        # Save output NDVI raster
        print(f"Saving: {dest_path}")
        ndvi.save(dest_path)
        print(f"Saved NDVI: {dest_path}")


def calc_mndwi(src_path, dest_path):
    if src_path.lower().endswith(".tif"):
        print(f"Processing mndwi: {src_path}")
        # Define output path
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Create Raster object
        in_raster = src_path
        # raster = arcpy.Raster(in_raster)

        # Band 2 = Green, Band 5 = SWIR (1-based indexing in ArcPy)
        green = arcpy.Raster(f"{in_raster}/Band_2")
        swir = arcpy.Raster(f"{in_raster}/Band_5")

        # Calculate MNDWI
        # MNDWI = (Green - SWIR) / (Green + SWIR)
        mndwi = (green - swir) / (green + swir)

        # Save output MNDWI raster
        print(f"Saving: {dest_path}")
        mndwi.save(dest_path)
        print(f"Saved MNDWI: {dest_path}")

index_gen_methods = { "NDVI": calc_ndvi, "MNDWI": calc_mndwi }

# index: NDVI, MNDWI
# name: Maximum, Median
# id_prefix: CSDC30_47, CSDC30_48
def get_algorithm(index, name, id_prefix):
    # path --> a directory containing multiple geotiff files
    filter_with_id_prefix = get_filter_with_id_prefix(id_prefix)
    fn = statistics_methods[name]
    if fn is None:
        print(f"Unknown algorithm: {name}")
        return None

    def algorithm(dir_name, src_root_dir, dest_root_dir):
        dir_path = os.path.join(src_root_dir, dir_name)
        print(f"Processing {name} for: {dir_path} ({id_prefix})")
        year = dir_path[-4:]
        if is_valid_dir(dir_path):
            paths = [os.path.join(dir_path, file) for file in os.listdir(dir_path) ]
            rs_array = [ path for path in paths if filter_with_id_prefix(path) ]
            if len(rs_array) == 0:
                print(f"no valid files in {dir_path}, skipping...")
                return

            # rule to generate output path
            output_path = os.path.join(dest_root_dir, f"{id_prefix}_{index}_{year}_{name}.tif")
            process_files(rs_array, output_path, fn)
    return algorithm


def process_files(arr_src_path, dest_path, fn):
    rs_array = [arcpy.Raster(path) for path in arr_src_path ]
    rc =arcpy.ia.RasterCollection(rs_array)
    dest_raster= fn(rc, extent_type="UnionOf", cellsize_type="MinOf", ignore_nodata=True, process_as_multiband=True)
    print(f"Saving: {dest_path}")
    dest_raster.save(dest_path)
    print(f"Saved: {dest_path}")

def is_valid_dir(path):
    if os.path.isdir(path) and  ends_with_valid_year(path):
        return True
    else:
        print(f"Not a valid directory: {path}")
        return False

def ends_with_valid_year(s, min_year=1900, max_year=2100):
    if len(s) < 4:
        return False

    last4 = s[-4:]
    if last4.isdigit():
        year = int(last4)
        return min_year <= year <= max_year
    return False

def walk_for_files(src_root_dir, dest_root_dir,  filter, index ):
    # Walk through the directory
    index_gen = index_gen_methods.get(index)
    if index_gen is None:
        print(f"Unknown index: {index} or handler not supported")
        return

    for dirpath, dirnames, filenames in os.walk(src_root_dir):
        for file in filenames:
            # print(f"Visiting: {dirpath} {file}")
            src_path = os.path.join(dirpath, file)
            if not filter or not filter(src_path):
                print(f"Not a valid file: {src_path}, skipping...")
                continue

            output_dir = dirpath.replace(src_root_dir, dest_root_dir)
            dest_path = os.path.join(output_dir, file.replace("TPG", "_" + index))
            # print(f"Processing: {src_path} --> {dest_path}")
            index_gen(src_path, dest_path)

def get_filter_with_id_prefix(prefix):
    def filter_func(path):
        if not os.path.isfile(path):
            return False
        if not path.lower().endswith(".tif"):
            return False
        if not os.path.basename(path).startswith(prefix):
            return False
        return True
    return filter_func

def walk_for_dirs(src_root_dir, dest_root_dir, mutilple_files_handler):
    # Walk through the directory
    if mutilple_files_handler is None:
        print("mutilple_files_handler is None, only support maximum and median statistics at this time.")
        return

    dirs = [ dir for dir in os.listdir(src_root_dir) if os.path.isdir(os.path.join(src_root_dir, dir))]
    for dir in dirs:
        src_dir = os.path.join(src_root_dir, dir)
        # print(f"Visiting: {src_root_dir}, {dir}")
        if ends_with_valid_year(src_dir):
            mutilple_files_handler(dir, src_root_dir, dest_root_dir )


if __name__ == "__main__":
    # Set the input and outpu directories
    # root_dir = "e:/zyc/csdc301/data"
    root_dir = "C:/Workspace/csdc/data"
    # index = "NDVI"
    index = "MNDWI"
    tpg_dir = os.path.join(root_dir, "tpt")
    temp_dir = os.path.join(root_dir, "temp")
    index_dir = os.path.join(root_dir, index)
    year_max_index_dir = os.path.join(root_dir, index + "_Maximum")
    year_median_index_dir = os.path.join(root_dir, index + "_Median")

    # id_prefixs = [ "CSDC30_47", "CSDC30_48" ]
    # or gernerate id_prefixs from tpg_dir or some other way
    id_prefixs = [ "CSDC30_47" ]

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Enable Spatial Analyst extension
    arcpy.CheckOutExtension("Spatial")
    # Set workspace and overwrite option
    arcpy.env.workspace = temp_dir
    arcpy.env.overwriteOutput = True

    ### uncomment the following steps you want

    # step1: calculate index(NDVI ...) for each TIFF file
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
    walk_for_files(
        src_root_dir=tpg_dir,  dest_root_dir = index_dir, filter=is_valid_tiff, index=index
    )

    # step2: calculate maximum and median index (NDVI ...) for each year
    for id_prefix in id_prefixs:
        #  calculate maximum NDVI for each year
        if not os.path.exists(year_max_index_dir):
            os.makedirs(year_max_index_dir)
        handle_maximum_with_id_prefix = get_algorithm(index, "Maximum", id_prefix)
        walk_for_dirs(
           src_root_dir= index_dir,
           dest_root_dir= year_max_index_dir,
           mutilple_files_handler=handle_maximum_with_id_prefix
        )

        # calculate median index (NDVI ...) for each year
        if not os.path.exists(year_median_index_dir):
            os.makedirs(year_median_index_dir)
        handle_median_with_id_prefix = get_algorithm(index, "Median", id_prefix)
        walk_for_dirs(
            src_root_dir=index_dir,
            dest_root_dir= year_median_index_dir,
            mutilple_files_handler=handle_median_with_id_prefix
        )

    try:
        if os.path.exists(temp_dir):
            # print(f"Directory {temp_dir} exists, removing it...")
            os.rmdir(temp_dir)
    except OSError as error:
        print(error)
        print(f"Directory {temp_dir} can not be removed" )

    # Release Spatial Analyst extension
    arcpy.CheckInExtension("Spatial")