# -*- coding: utf-8 -*-
import os
from datetime import datetime
from datetime import date

import numpy as np
import rasterio as rio

class FormatConvertor:
    def __init__(self ):
        self.year = 0
        self.mon = 0
        self.day = 0

    def Tiff2Serial(self, path):
        width = 0
        height = 0
        with rio.open(path)  as dataset:
            # print(dataset.profile)
            width = dataset.width
            height = dataset.height

            band_index = (8,9)
            rawData = dataset.read(band_index)
            # print(rawData.shape)
            # print(dataset.indexes)

            yearDestDir = os.path.join(self.destDir, str(self.year))
            if not os.path.exists(yearDestDir):
                os.makedirs(yearDestDir, exist_ok=True)

            theDay = date(self.year, self.mon, self.day)
            firstDayOfYear = date(self.year, 1, 1)
            doy = (theDay - firstDayOfYear).days + 1

            for i in range(height):
                rowDir = os.path.join(yearDestDir, "{0:0>4}".format(i))
                if not os.path.exists(rowDir):
                    os.makedirs(rowDir, exist_ok=True)

                for j in range(width):
                    lon,lat = dataset.transform * (i, j)
                    ndvi = rawData[0][i][j] / 10000.0
                    evi = rawData[1][i][j]  / 10000.0
                    if not (ndvi == 0 and evi ==0):
                        self.outputRecord(theDay, doy, i, j, lon, lat,  ndvi, evi)
                    # prin(lon, lat,rawData[0][i][j], rawData[1][i][j])
                    #

    def outputRecord(self, day, doy, i, j, lon, lat, ndvi, evi):
        file = "ndvi-{year}-{locx}-{locy}.txt".format(year=self.year, locx="{0:0>4}".format(i), locy="{0:0>4}".format(j))


        path = os.path.join(self.destDir, str(self.year), "{0:0>4}".format(i), file)
        # print(path)
        # date    DOY     NDVI     EVI
        with open(path, "a+") as fo:
            rec = "{day}\t{doy}\t{locx}\t{locy}\t{lon}\t{lat}\t{ndvi}\t{evi}\n" \
            .format(day=day.strftime("%m/%d/%y"),doy=doy, locx=i, locy=j, lon=lon, lat=lat, ndvi=ndvi, evi=evi)
            fo.write(rec)

    def batchTiff2Serials(self, srcDir, destDir):
        if not os.path.exists(srcDir):
            print('Error: input dir does not exist!')
            return

        if not os.path.exists(destDir):
            os.makedirs(destDir)
        elif len(os.listdir(destDir) ) > 0:
            print('Error: output dir will not be overridded!\nBackup first and run again plz!')
            return

        self.destDir = destDir
        files = sorted(os.listdir(srcDir))
        for file in files:
            path  = os.path.join(srcDir, file)
            if file.endswith('.tif'):
                strDate = file.split("-")[1]
                self.year = int(strDate[:4])
                self.mon =  int(strDate[4:6])
                self.day = int(strDate[6:8])

                print("Tiff2Serial: processing {0}...".format(file))
                self.Tiff2Serial(path)

fc = FormatConvertor()
fc.batchTiff2Serials('/Users/jiangzhu/workspace/igsnrr/data/ndvi/samples',
                     '/Users/jiangzhu/workspace/igsnrr/data/ndvi/serials')

