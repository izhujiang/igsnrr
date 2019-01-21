from netCDF4 import Dataset
from datetime import date, timedelta
import numpy as np

def CalculateYearValues(srcPath, destPath, ele):
    # read and caculate average
    scr_root_grp = Dataset(srcPath)
    src_val = scr_root_grp.variables[ele]
    years = int(len(src_val) / 12);

    rootgrp = CreateCruNetCDF(destPath, ele, False)
    vals = rootgrp.variables[ele]

    year_init = 1991

    for i in range(years ):
        sub = src_val[i*12: (i+1)*12]
        # for pet element to caculate monthly evapotranspiration
        if ele == "pet":
            for j in range(1,13):
                y = year_init + i
                m = j
                thisMon = date(y, m  , 1)

                if j == 12:
                    y += 1
                    m = 1
                else:
                    m = j +1

                nextMon = date(y, m , 1)
                days = (nextMon - thisMon).days
                sub[j -1] = sub[j -1] * days
        # print(type(np.sum(sub)))
        # year_pet = np.ndarray(shape=( 360, 720), dtype=float)
        year_val = np.sum(sub, axis=0)
        vals[i,:,:] = year_val

    # from numpy.random import uniform
    # vals[0:5,:,:] = uniform(size=(5,nlats,nlons))
    # print(vals[0:2, :, :])

    # print(rootgrp.variables)
    rootgrp.close()


def CalculateYearAverage(srcPath, destPath, ele):
    scr_root_grp = Dataset(srcPath)
    src_val = scr_root_grp.variables[ele]

    rootgrp = CreateCruNetCDF(destPath, ele, True)
    vals = rootgrp.variables[ele]

    # calc average of year 1901-2006, because of errors in orginal
    # data[2007.08-...]
    # sub = src_val[0: 105]
    sub = src_val
    vals[0, :, :] = np.average(sub, axis=0)

    # vals[0:5,:,:] = uniform(size=(5,nlats,nlons))
    # print(vals[0:2, :, :])

    rootgrp.close()


def CreateCruNetCDF(destPath, ele, isAve=False):
    # save average to nc file
    rootgrp = Dataset(destPath, "w")
    time = None
    if isAve == True:
        time = rootgrp.createDimension("time", 1)
    else:
        time = rootgrp.createDimension("time", 2017 - 1900 + 1)

    lat = rootgrp.createDimension("lat", 360)
    lon = rootgrp.createDimension("lon", 720)

    times = rootgrp.createVariable("time","f8",("time",))
    times.long_name = "time"
    if isAve == True:
        times.units = "";
    else:
        # times.units = "years since 1900"
        times.units = 1

    times.calendar = "gregorian"

    latitudes = rootgrp.createVariable("lat","f4",("lat",))
    latitudes.long_name = "latitude";
    latitudes.units = "degrees_north";

    longitudes = rootgrp.createVariable("lon","f4",("lon",))
    longitudes.long_name = "longitude";
    longitudes.units = "degrees_east";

    # two dimensions unlimited
    vals = rootgrp.createVariable(ele, "f8",("time","lat","lon",), fill_value=9.96921E36)
    vals.long_name = "potential evapotranspiration";
    vals.units = "mm/year";
    vals.correlation_decay_distance = -999.0; # float
    vals.missing_value = 9.96921E36; # float

    lats =  np.arange(-89.75,90,.5)
    lons =  np.arange(-179.75,180,.5)
    latitudes[:] = lats
    longitudes[:] = lons
    # print("latitudes =\n",latitudes[:])

    # nlats = len(rootgrp.dimensions["lat"])
    # nlons = len(rootgrp.dimensions["lon"])
    return rootgrp;

if __name__ == "__main__":
    srcFile = "../../../data/cru/cru_ts4.02.1901.2017.pet.dat.nc"
    sumFile = "../../../data/cru/cru_ts4.02.1901.2017.pet.year.nc"
    avgFile = "../../../data/cru/cru_ts4.02.1901.2017.pet.avg.nc"
    CalculateYearValues(srcFile, sumFile, "pet")
    CalculateYearAverage(sumFile, avgFile, "pet")

    # uncomment the following code to run for "precipication" element
    srcFile = "../../../data/cru/cru_ts4.02.1901.2017.pre.dat.nc"
    sumFile = "../../../data/cru/cru_ts4.02.1901.2017.pre.year.nc"
    avgFile = "../../../data/cru/cru_ts4.02.1901.2017.pre.avg.nc"
    CalculateYearValues(srcFile, sumFile, "pre")
    CalculateYearAverage(sumFile, avgFile, "pre")

