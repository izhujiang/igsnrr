
# -*- coding: utf-8 -*-
import os
import rasterio

dataRoot = '/Users/jiangzhu/workspace/igsnrr/data/MOD13Q1'
inputDir = os.path.join(dataRoot, 'MOD13Q1-MEDIAN-XJ')
outputDir = os.path.join(dataRoot, 'MOD13Q1-MEDIAN-XJ-join')
if not os.path.exists(outputDir):
    os.makedirs(outputDir)

files = sorted(os.listdir(inputDir))

fInput = os.path.join(inputDir, files[0])
profile = None
with rasterio.open(fInput) as dt_in:
    profile = dt_in.profile.copy()
    profile.update({
            'count': len(files),
            'dtype': 'float32',
            'height': dt_in.height,
            'width': dt_in.width
            })
fOutput = os.path.join(outputDir, 'MOD13Q1-MEDIAN-XJ-join.tif')

with rasterio.open(fOutput, 'w', **profile) as dt_out:
    year_index = 1

    for fInput in files:
        fInput = os.path.join(inputDir, fInput)
        print(fInput)
        with rasterio.open(fInput) as dt_in:
            ndvi_arr = dt_in.read(1)
            dt_out.write_band(year_index, ndvi_arr)
            year_index += 1