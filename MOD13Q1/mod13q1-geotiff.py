# -*- coding: utf-8 -*-
import os
import numpy as np
import statsmodels.api as sm
import rasterio
from enum import Enum
import argparse
import json
from datetime import datetime, timedelta
import mkt

AnalysisMethood = Enum('Mothod', ('OLS', 'MANKENDALL', 'UNKNOWN'))

# calc whole grid
def analyzeGrid(fInput, opts, outputDir, fOutputPrefix, method):
    profile = None
    debug_infos = []
    with rasterio.open(fInput) as dt_in:
        profile = dt_in.profile.copy()
        ndvi_arr = dt_in.read()
        zlen, height, width = ndvi_arr.shape
        # print(ndvi_arr.shape)
        x = range(2000, 2000 + zlen)

        # fill the buf for storing analysis result
        bands_data, bands_desc = initResultStorage(method, (height, width), dt_in.nodata)
        profile.update({
                # 'count': len(bands_data),
                'count': 1,
                'dtype': 'float32',
                'height': height,
                'width': width,
                })
        # fill the buf store analysis result per single point
        # for i in range(int(height/2-100), int(height/2)):
            # for j in range(int(width/2-100), int(width/2)):
        t1 = datetime.now()
        for i in range(args.top, args.bottom):
            for j in range(args.left, args.right):
                y = ndvi_arr[:, i, j]
                if not np.isnan(np.min(y)):
                    resInPnt = analyzeSinglePoint(x, y, method)
                    # print("\nvalue at point (%d, %d)\n".format(i, j), resInPnt)
                    for (k, vArray) in  bands_data.items():
                        vArray[i, j] = resInPnt[k]
                    if args.debug:
                        debug_infos.append({'loc_i':i, 'loc_j':j, 'v': y.tolist(), 'ana': resInPnt})
                else:
                    for (k, vArray) in  bands_data.items():
                        vArray[i, j] = dt_in.nodata
        t2 = datetime.now()
        print("analyzing {0} line takes {1} seconds.\n".format((args.bottom - args.top),(t2-t1).seconds))

    for (k, vArray) in  bands_data.items():
        fOutput = os.path.join(outputDir, fOutputPrefix + k + ".tiff")
        with rasterio.open( fOutput, 'w', **profile) as dt_out:
            layerIndex = 1
            dt_out.write_band(layerIndex, vArray)
                # dt_out.set_band_description(layerIndex, bands_desc[k])
                # layerIndex += 1

    flog = os.path.join(outputDir, 'debug_info.txt')
    with open(flog, 'w') as fo:
        for rec in debug_infos:
            json_string = json.dumps(rec) + "\n"
            fo.writelines([json_string])
        fo.flush()


# init buffer for storing analysis result
def initResultStorage(method, shape, nodata ):
    bands_data = {}
    bands_desc = {}
    if method == AnalysisMethood.OLS:
        bands_data = {
            'b0': np.full(shape, nodata, np.float32),
            'b1': np.full(shape, nodata, np.float32),
            'rsquared': np.full(shape, nodata, np.float32),
            'p0': np.full(shape, nodata, np.float32),
            'p1': np.full(shape, nodata, np.float32),
            'f': np.full(shape, nodata, np.float32),
            't0': np.full(shape, nodata, np.float32),
            't1': np.full(shape, nodata, np.float32),
        }
        bands_desc = {
            'b0': "coef b0",
            'b1': "coef b1",
            'rsquared': "R-squared",
            'p0': "P>|t| (P0)",
            'p1': "P>|t| (P1)",
            'f': "F-statistic",
            't0': "tValue t0",
            't1': "tValue t1",
       }
    elif method == AnalysisMethood.MANKENDALL:
        bands_data = {
            'ha': np.full(shape, nodata, np.float32),
            'm': np.full(shape, nodata, np.float32),
            'c': np.full(shape, nodata, np.float32),
            'p': np.full(shape, nodata, np.float32),
        }
        bands_desc = {
            'ha': "result of the statistical test indicating whether or not to accept hte alternative hypothesis ‘Ha’",
            'm': "slope of the linear fit",
            'c': "intercept of the linear fit",
            'p': "p-value of the obtained Z-score statistic",
       }
    else:
        print("unknown analysis method")
    return bands_data, bands_desc

# calc single point
def analyzeSinglePoint(x, y, method):
    res = {}
    if method == AnalysisMethood.OLS:
        x = sm.add_constant(x)
        model = sm.OLS(y, x)
        results = model.fit()
        # print(x, results.summary())
        res = {
            'b0': results.params[0],
            'b1': results.params[1],
            'rsquared': results.rsquared,
            'p0': results.pvalues[0],
            'p1': results.pvalues[1],
            'f': results.fvalue,
            't0': results.tvalues[0],
            't1': results.tvalues[1],
        }
        # print(res)
    elif method == AnalysisMethood.MANKENDALL:
        # get the slope, intercept and pvalues from the mklt module
        ALPHA = 0.01
        MK, m, c, p = mkt.test(x, y, eps=1E-3, alpha=ALPHA, Ha="upordown")

        ha = 1
        if MK.startswith('rej'):
            ha = 0
        # ha = not MK.startswith('reject')

        res = {
            'ha':ha,
            'm': m,
            'c': c,
            'p': p,
        }
    else:
        print("unknown analysis method")

    return res

# main entry
debugSinglePoint = False

if debugSinglePoint == True: # for debug in single point
    # for debug sinle point
    x = np.array(list(range(2000, 2020)))
    y = np.array([1447, 1580, 2037, 1779.9266, 1398.0007, 1614.4379, 1493.4379,
            1580, 1613, 1728.7712, 1630.695, 1516.4379, 1775.1046, 1434.4379,
            1383.695, 1720.7784, 1664, 1578.9172, 1711.4103, 1691])
    # analyzeSinglePoint(x, y, AnalysisMethood.OLS)
    analyzeSinglePoint(x, y, AnalysisMethood.MANKENDALL)
else:
    parser = argparse.ArgumentParser(description="Analysis program for mod13q1 in geotiff format")
    parser.add_argument("method",
                        help="method(OLS, MANKENDALL) for analyze modis13q1 data")
    parser.add_argument("src",
                        help="input geotiff file for analysis")
    parser.add_argument("top", type=int,
                        help="top of extent")
    parser.add_argument("bottom", type=int,
                        help="bottom of extent")
    parser.add_argument("left", type=int,
                        help="left of extent")
    parser.add_argument("right", type=int,
                        help="right of extent")
    parser.add_argument("destDir",
                        help="output directory to store analysis results")
    parser.add_argument("-d", "--debug", action="store_true",
                    help="for debug")

    args = parser.parse_args()
    print(args)

    # define input and output
    # dataRoot = '/Users/jiangzhu/workspace/igsnrr/data/MOD13Q1'
    # inputDir = os.path.join(dataRoot, 'MOD13Q1-MEDIAN-join')
    # outputDir = os.path.join(dataRoot, 'MOD13Q1-MEDIAN-out')
    fInput = args.src
    outputDir = args.destDir
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    # fInput = os.path.join(inputDir, 'MOD13Q1-MEDIAN-join.tif')
    # fOutput = os.path.join(outputDir, 'MOD13Q1-MEDIAN-ana.tif')
    fOutputPrefix = "MOD13Q1-MEDIAN-ana_"

    method = AnalysisMethood.UNKNOWN
    if args.method == "OLS":
        method = AnalysisMethood.OLS
    elif args.method == "MANKENDALL":
        method = AnalysisMethood.MANKENDALL
    else:
        method = AnalysisMethood.UNKNOWN
    analyzeGrid(fInput, args, outputDir, fOutputPrefix, method)
