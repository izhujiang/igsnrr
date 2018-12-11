#!/usr/bin/env python

import time
from netCDF4 import Dataset
import numpy as np
# import matplotlib.pyplot as plt

def sumCruPre():
    sourceFile = "../../../data/cru/cru_ts4.02.1901.2017.pet.dat.nc"
    sumFile = "../../../data/cru/cru_ts4.02.1901.2017.pet.year.nc"

    # read and caculate average
    scr_root_grp = Dataset(sourceFile)
    pet = scr_root_grp.variables['pet']
    # lats = scr_root_grp.variables['lat']
    # lons = scr_root_grp.variables['lon']
    years = int(len(pet) / 12);
    # years_pet = np.ndarray(shape=(years, 360, 720), dtype=float)

    sum_root_grp = createCruPreYear(sumFile)
    # year_sum_pet = sum_root_grp.variables['pet']
    # print(years)
    for i in range(years):
        sub = pet[i*12: (i+1)*12]
        # print(type(np.sum(sub)))

        year_pet = np.ndarray(shape=( 360, 720), dtype=float)
        year_pet = np.sum(sub)
        print(year_pet)
        # year_sum_pet[i, :, :] = year_pet

    # print(sum_root_grp)
    # sum_root_grp.close()

        # print(years_temp[i])

    # avg = np.average(years_pet)
    # print(avg)

    # save average to nc file

def createCruPreYear(path):
    rootgrp = Dataset(path, 'w', format='NETCDF4')

    # dimensions
    t = rootgrp.createDimension("time", None)
    # lat = rootgrp.createDimension("lat", 360)
    # lon = rootgrp.createDimension("lon", 720)
    rootgrp.createDimension('lat', 72)
    rootgrp.createDimension('lon', 144)

    rootgrp.description = "cru precipitation yearly average 1991-2017"
    rootgrp.history = "Created " + time.ctime(time.time())
    rootgrp.source = "CRU TS4.02 Potential Evapotranspiration"

    # variables
    times = rootgrp.createVariable("time","f8",("time",))
    latitudes = rootgrp.createVariable('lat', 'f4', ('lat',))
    longitudes = rootgrp.createVariable('lon', 'f4', ('lon',))
    pet = rootgrp.createVariable('pet', 'f4', ('time', 'lat', 'lon',))

    latitudes.long_name = "latitude";
    latitudes.units = "degrees_north"

    longitudes.long_name = "longitude"
    longitudes.units = "degrees_east"

    times.units = "year since 1901"
    times.calendar = "gregorian"

    pet.long_name = "potential evapotranspiration"
    pet.units = "mm/year"
    # pet._FillValue = 9.96921E36
    # pet.missing_value = 9.96921E36

    # data
    # lats =  np.arange(-89.75, 90.25, .5)
    # lons =  np.arange(-179.75, 180.25, .5)
    lats =  np.arange(-90, 90, 2.5)
    lons =  np.arange(-180, 180, 2.5)
    latitudes = lats
    longitudes = lons
    for i in range(5):
        pet[i,:,:] = np.random.uniform(size=(len(lats), len(lons)))
    print(longitudes, latitudes)
    print(pet[2])
    rootgrp.close()


    return rootgrp



if __name__ == "__main__":
    sumCruPre()
