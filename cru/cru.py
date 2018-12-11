from netCDF4 import Dataset
import numpy

# rootgrp = Dataset("../../../data/cru/cru_ts4.02.1901.2017.pet.dat.nc")
rootgrp = Dataset("../../../data/cru/testdat.nc", "w")
# fcstgrp = rootgrp.createGroup("forecasts")
# analgrp = rootgrp.createGroup("analyses")
level = rootgrp.createDimension("level", None)
time = rootgrp.createDimension("time", None)
lat = rootgrp.createDimension("lat", 360)
lon = rootgrp.createDimension("lon", 720)

times = rootgrp.createVariable("time","f8",("time",))
levels = rootgrp.createVariable("level","i4",("level",))
latitudes = rootgrp.createVariable("lat","f4",("lat",))
longitudes = rootgrp.createVariable("lon","f4",("lon",))
# two dimensions unlimited
temp = rootgrp.createVariable("temp","f4",("time","level","lat","lon",))

lats =  numpy.arange(-89.75,90,.5)
lons =  numpy.arange(-179.75,180,.5)
latitudes[:] = lats
longitudes[:] = lons
# print("latitudes =\n",latitudes[:])

nlats = len(rootgrp.dimensions["lat"])
nlons = len(rootgrp.dimensions["lon"])
from numpy.random import uniform
temp[0:5,0:10,:,:] = uniform(size=(5,10,nlats,nlons))
print(temp[0:2, 0, :, :])
levels[:] =  [1000.,850.,700.,500.,300.,250.,200.,150.,100.,50.]

# print(rootgrp.variables)
rootgrp.close()
