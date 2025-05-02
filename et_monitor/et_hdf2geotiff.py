import h5py
import arcpy
import os

correct_modis_wkt = """
PROJCS["MODIS_Sinusoidal",
    GEOGCS["GCS_Sphere",
        DATUM["D_Sphere",
            SPHEROID["Sphere",6371007.181,0.0]],
        PRIMEM["Greenwich",0.0],
        UNIT["Degree",0.0174532925199433]],
    PROJECTION["Sinusoidal"],
    PARAMETER["False_Easting",0.0],
    PARAMETER["False_Northing",0.0],
    PARAMETER["Central_Meridian",0.0],
    UNIT["Meter",1.0]]
"""
def convert_hdf5_to_geotiff(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_name in os.listdir(input_dir):
        if file_name.endswith(".h5"):
            input_file = os.path.join(input_dir, file_name)

            with h5py.File(input_file, 'r') as hdf:
                if "ET" not in hdf:
                    # print(f"ET dataset not found in {file_name}. Skipping.")
                    print("ET dataset not found in {} . Skipping.".format(file_name))

                    continue
                et_data = hdf["ET"][:].transpose()
                # print(f"Processing {file_name}: ET shape = {et_data.shape}")
                print("Processing {}: ET shape = {} ".format(file_name, et_data.shape))

                projection_para = hdf.attrs.get("ProjectionPara", None)
                projection_str = hdf.attrs.get("ProjectionStr", None)
                up_left = hdf.attrs.get("UpLeft", None)
                low_right = hdf.attrs.get("LowRight", None)

                # Check if attributes are missing
                if projection_para is None or projection_str is None or up_left is None or low_right is None:
                    # print(f"Missing required attributes in {file_name}. Skipping.")
                    print("Missing required attributes in {} . Skipping.".format(file_name))
                    continue

                if isinstance(projection_str, bytes):
                    projection_str = projection_str.decode("utf-8")

                # try:
                #     ul_lat, ul_lon = up_left  # Assuming up_left is [latitude, longitude]
                #     lr_lat, lr_lon = low_right  # Assuming low_right is [latitude, longitude]
                # except ValueError:
                #     print(f"Invalid UpLeft or LowRight attributes in {file_name}. Skipping.")
                #     continue

                # caustions: the order of projection parameters are upper_left_y, pixel_width, _, upper_left_x, _, pixel_height in ETMonitor.DailyET.2021365.h25v04.v001.h5
                # upper_left_x, pixel_width, _, upper_left_y, _, pixel_height = map(float, projection_para.split())
                upper_left_y, pixel_width, _, upper_left_x, _, pixel_height = map(float, projection_para.split())
                num_rows, num_cols = et_data.shape
                lower_right_x = upper_left_x + (pixel_width * num_cols)
                lower_right_y = upper_left_y - (abs(pixel_height) * num_rows)
                # print("upper_left_x:", upper_left_x)
                # print("upper_left_y:", upper_left_y)
                # print("lower_right_x:", lower_right_x)
                # print("lower_right_y:", lower_right_y)

                # Prepare spatial reference and extent
                spatial_ref = arcpy.SpatialReference()

                # Define CRS
                try:
                    spatial_ref.loadFromString(projection_str)
                except ValueError:
                    # print(f"Warning: error in parsing WKT: {projection_str}. Using default MODIS WKT.")
                    print("Warning: error in parsing WKT: {}. Using default MODIS WKT.".format(projection_str))
                    spatial_ref.loadFromString(correct_modis_wkt)

                extent = arcpy.Extent(upper_left_x, lower_right_y, lower_right_x, upper_left_y)

                raster = arcpy.NumPyArrayToRaster(
                    et_data,
                    arcpy.Point(upper_left_x, lower_right_y), # left_bottom point
                    pixel_width,
                    abs(pixel_height),
                    value_to_nodata=-1  # Assuming -1 is nodata, adjust as needed
                )
                arcpy.DefineProjection_management(raster, spatial_ref)

                # Save to GeoTIFF
                output_file = os.path.join(output_dir, file_name.replace(".h5", ".tif"))
                raster.save(output_file)
                # print(f"Saved GeoTIFF to {output_file}")
                print("Saved GeoTIFF to {}".format(output_file))


# Example usage
input_directory = os.path.join(os.getcwd(), "data2")
output_directory = os.path.join(os.getcwd(), "data3")
convert_hdf5_to_geotiff(input_directory, output_directory)