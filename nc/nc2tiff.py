import os.path as path
from netCDF4 import Dataset
import rasterio

def NetCDF2Tiff(data_dir, fname, **kwargs):
    fn = path.join(data_dir, fname)
    with Dataset(fn, "r", format="NETCDF4") as ds:
        # print("Dimensions:")
        # for dimobj in ds.dimensions.values():
        #     print(dimobj)

        # print("\nVariables:")
        vLon = ds.variables[kwargs['LON']]
        vLat = ds.variables[kwargs['LAT']]
        if vLon is None or len(vLon.shape) != 1 or vLat is None or len(vLat.shape) != 1:
            print("Lon or Lat Variable Error: ", vLon, vLat)
            return

        west = vLon[0]
        north = vLat[0]
        xsize = abs((vLon[-1] - vLon[0])) / (len(vLon[:]) - 1)
        ysize = abs((vLat[-1] - vLat[0])) / (len(vLat[:]) - 1)
        transform = rasterio.transform.from_origin(west, north, xsize, ysize)

        for vk in ds.variables.keys():
            # print(vk)
            cvar = ds.variables[vk]

            if len(cvar.shape) == 1:
                if cvar.name == kwargs['LON']:
                    # print("lon:")
                    # print(cvar[:])
                    pass
                elif cvar.name == kwargs['LAT']:
                    # print("lat:")
                    # print(cvar[:])
                    pass
                else:
                    print("invalid variable:" + cvar.name)
            elif len(cvar.shape) == 2:
                z_data = cvar[:]
                profile = {
                    'driver': 'GTiff',
                    'height': z_data.shape[0],
                    'width': z_data.shape[1],
                    'count': 1,
                    # 'dtype': rasterio.uint8
                    'dtype': z_data.dtype,
                    'tiled': True,
                    'blockxsize': 256,
                    'blockysize': 256,
                    'compress': 'lzw',
                    'nodata': cvar.Fill_value,
                    'crs': 'EPSG:4326',
                    'transform': transform,
                    }
                tiff_fname = fname.replace(".nc", "-" + vk + ".tif")
                tiff_path = path.join(data_dir, tiff_fname)
                with rasterio.open(tiff_path, 'w', **profile) as dst:
                    dst.write(z_data, 1)
                    dst.update_tags(**cvar.__dict__)
                    # print(dst.tags())

    # end of reading nc file
    # ds.close()

if __name__ == "__main__":
    data_dir = "/Users/jiangzhu/workspace/igsnrr/data/nc/"
    # fname = "CN-Reanalysis-yearly-2018010100.nc"
    fname = "2019.nc"

    contex = {
        'LAT': "Lat",
        'LON': "Lon"
        }

    print("processing file: {0} ...".format(fname))
    NetCDF2Tiff(data_dir, fname, **contex)

    print("done!")