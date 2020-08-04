# -*- coding: utf-8 -*-
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import rasterio
from enum import Enum
import argparse
import json
from datetime import datetime
import mkt
import piecewise as pw
import math
import multiprocessing as mp


class AnalysisMethood(Enum):
    OLS = 1,
    MANNKENDALL = 2,
    PIECEWISE = 4,
    MAX = 8,
    UNKNOWN = 256


# calc whole grid
def analyzeGrid(fInput, opts, outputDir, fOutputPrefix, method):
    runMode = "multipleprocess"
    # runMode = "singleprocess"
    with rasterio.open(fInput) as dt_in:
        profile = dt_in.profile.copy()
        # print(profile)
        # print(dt_in.descriptions)

        width = profile['width']
        height = profile['height']
        cpu_num = int(mp.cpu_count())
        # cpu_num = 4
        step = math.ceil(height / cpu_num)

        if runMode == "singleprocess":
            print("running single process mode ... ")
            for i in range(cpu_num):
                line_start = i * step
                line_end = min(line_start + step, height)
                chunk_opts = opts.copy()
                chunk_opts["line_start"] = line_start
                chunk_opts["line_end"] = line_end
                analyzeChunk(
                        "{:03d}".format(i+1), fInput, chunk_opts, outputDir,
                        fOutputPrefix, method)
        else:
            print("running multiprocessing mode using pool.apply_async with \
            {0} cpus ...".format(cpu_num))
            mp.freeze_support()
            pool = mp.Pool(cpu_num)
            for i in range(cpu_num):
                line_start = i * step
                line_end = min(line_start + step, height)
                chunk_opts = opts.copy()
                chunk_opts["line_start"] = line_start
                chunk_opts["line_end"] = line_end
                pool.apply_async(
                        analyzeChunk, args=(
                            "{:03d}".format(i+1),
                            fInput,
                            chunk_opts,
                            outputDir,
                            fOutputPrefix,
                            method)
                        )
            pool.close()
            pool.join()

        # combine parts into whole files
        for root, dirs, _ in os.walk(outputDir, topdown=False):
            for name in dirs:
                cur_dir = os.path.join(root, name)
                part_arr = []
                for part_file in sorted(os.listdir(cur_dir)):
                    with rasterio.open(
                            os.path.join(cur_dir, part_file)) as partfile_in:
                        part_data = partfile_in.read(1)
                        part_arr.append(part_data)

                # print(part_arr[0].shape, part_arr[3].shape)
                data = np.vstack(tuple(part_arr))

                fOutput = os.path.join(root,  cur_dir + ".tiff")
                profile.update({
                        # 'count': len(bands_data),
                        'count': 1,
                        'dtype': 'float32',
                        'height': height,
                        'width': width,
                        })
                with rasterio.open(fOutput, 'w', **profile) as dt_out:
                    layerIndex = 1
                    # dt_out.nodata = dt_in.nodata
                    dt_out.write_band(layerIndex, data)


def analyzeChunk(chunkId, fInput, opts, outputDir, fOutputPrefix, method):
    '''
    analyzeChunk
    '''
    profile = None
    debug_infos = []
    print("processing ", chunkId, opts)

    with rasterio.open(fInput) as dt_in:
        profile = dt_in.profile.copy()
        # window = Window(col_off, row_off, width, height)
        width = profile["width"]
        height = opts["line_end"] - opts["line_start"]
        chunk_win = rasterio.windows.Window(
                0, opts["line_start"], width, height)
        ndvi_arr = dt_in.read(window=chunk_win)
        # msk = dt_in.read_masks(1)
        zlen, height, width = ndvi_arr.shape
        # print(ndvi_arr.shape)
        x = np.arange(opts["timeStart"], opts["timeStart"] + zlen)

        # fill the buf for storing analysis result
        bands_data, bands_desc = initResultStorage(
                method, (height, width), dt_in.nodata)
        # mask = dt_in.dataset_mask()
        # print(mask)
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

        for i in range(0, height):
            if i % 50 == 0:
                print(
                        "processing line : {0} at {1}".format(
                            i + opts["line_start"], datetime.now()))

            for j in range(0, width):
                y = ndvi_arr[:, i, j]
                if not np.isnan(np.min(y)):
                    resInPnt = analyzeSinglePoint(x, y, method)
                    for k in resInPnt:
                        bands_data[k][i, j] = resInPnt[k]
                    # for (k, vArray) in  bands_data.items():
                    #     vArray[i, j] = resInPnt[k]
                    if opts["debug"]:
                        debug_infos.append({
                                    'loc_i': i, 'loc_j': j,
                                    'v': y.tolist(), 'ana': resInPnt})
                else:
                    for (k, vArray) in bands_data.items():
                        # vArray[i, j] = np.nan
                        # vArray[i, j] = dt_in.nodata
                        vArray[i, j] = -9999

        t2 = datetime.now()
        print("analyzing {0} line takes {1} seconds.".format(
            height, (t2-t1).seconds))

    abspath = os.path.abspath(fInput)
    _, fname = os.path.split(abspath)
    fprefix, _ = os.path.splitext(fname)
    # output analysis result into multiple tiff files
    for (k, vArray) in bands_data.items():
        k_dir = os.path.join(outputDir, fprefix + "-" + k)
        if not os.path.exists(k_dir):
            os.makedirs(k_dir)
        fOutput = os.path.join(k_dir, chunkId + ".tiff")
        with rasterio.open(fOutput, 'w', **profile) as dt_out:
            layerIndex = 1
            # dt_out.nodata = dt_in.nodata
            dt_out.nodata = -9999
            dt_out.write_band(layerIndex, vArray)
            # dt_out.write_mask(msk)
            # dt_out.set_band_description(layerIndex, bands_desc[k])
            # layerIndex += 1

    # write debug info into txt file
    if opts["debug"]:
        flog = os.path.join(outputDir, 'debug_info.txt')
        with open(flog, 'w') as fo:
            for rec in debug_infos:
                json_string = json.dumps(rec) + "\n"
                fo.writelines([json_string])
            fo.flush()


# init buffer for storing analysis result
def initResultStorage(method, shape, nodata):
    bands_data = {}
    bands_desc = {}
    if method == AnalysisMethood.OLS:
        bands_data = {
            'b0': np.full(shape, nodata, np.float32),
            'b1': np.full(shape, nodata, np.float32),
            'r2': np.full(shape, nodata, np.float32),
            'p0': np.full(shape, nodata, np.float32),
            'p1': np.full(shape, nodata, np.float32),
            'f': np.full(shape, nodata, np.float32),
            't0': np.full(shape, nodata, np.float32),
            't1': np.full(shape, nodata, np.float32),
            }
        bands_desc = {
            'b0': "coef b0",
            'b1': "coef b1",
            'r2': "R-squared",
            'p0': "P>|t| (P0)",
            'p1': "P>|t| (P1)",
            'f': "F-statistic",
            't0': "tValue t0",
            't1': "tValue t1",
            }
    elif method == AnalysisMethood.MANNKENDALL:
        bands_data = {
            'zmk': np.full(shape, nodata, np.float32),
            'ha': np.full(shape, nodata, np.float32),
            'm': np.full(shape, nodata, np.float32),
            'c': np.full(shape, nodata, np.float32),
            'p': np.full(shape, nodata, np.float32),
        }
        bands_desc = {
            'zmk': "the Z-score based on above estimated mean and variance",
            'ha': "result of the statistical test indicating whether \
                    or not to accept hte alternative hypothesis ‘Ha’",
            'm': "slope of the linear fit",
            'c': "intercept of the linear fit",
            'p': "p-value of the obtained Z-score statistic",
        }
    elif method == AnalysisMethood.PIECEWISE:
        bands_data = {
            'NS': np.full(shape, nodata, np.float32),
            'ceof': np.full(shape, nodata, np.float32),
            'S1': np.full(shape, nodata, np.float32),
            'S2': np.full(shape, nodata, np.float32),
            'S3': np.full(shape, nodata, np.float32),
            'S4': np.full(shape, nodata, np.float32),
            'b1': np.full(shape, nodata, np.float32),
            'b2': np.full(shape, nodata, np.float32),
            'b3': np.full(shape, nodata, np.float32),
            'b4': np.full(shape, nodata, np.float32),
            'b5': np.full(shape, nodata, np.float32),
        }
        bands_desc = {
            'NS': "segements count",
            'ceof': "correlation coefficient",
            'S1': "first segment point",
            'S2': "second segment point",
            'S3': "third segment point",
            'S4': "forth segment point",
            'b1': "first segment slope",
            'b2': "second segment slope",
            'b3': "third segment slope",
            'b4': "forth segment slope",
            'b5': "fifth segment slope"
         }
    elif AnalysisMethood.MAX:
        bands_data = {
            'max': np.full(shape, nodata, np.float32),
        }
        bands_desc = {
            'max': "maximum vale",
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
            'r2': results.rsquared,
            'p0': results.pvalues[0],
            'p1': results.pvalues[1],
            'f': results.fvalue,
            't0': results.tvalues[0],
            't1': results.tvalues[1],
        }
        # print(res)
    elif method == AnalysisMethood.MANNKENDALL:
        # get the slope, intercept and pvalues from the mklt module
        ALPHA = 0.05
        Zmk, MK, m, c, p = mkt.test(x, y, eps=1E-3, alpha=ALPHA, Ha="upordown")

        ha = 1
        if MK.startswith('rej'):
            ha = 0
        # ha = not MK.startswith('reject')
        res = {
            'zmk': Zmk,
            'ha': ha,
            'm': m,
            'c': c,
            'p': p,
        }
    elif method == AnalysisMethood.PIECEWISE:
        data = {'T': x, 'Y': y}
        df = pd.DataFrame.from_dict(data)
        nrow, _ = df.shape

        numPotentials = 10
        maxFirstInflection = nrow - 1
        minLastInflection = 2
        rollingWinSize = 5
        fixedPointRate = 0.3

        ctx = pw.PieceWiseLinearRegressionContext(
            recordNumber=nrow,
            minSegmentCount=1,
            maxSegmentCount=3,
            maxFirstInflection=maxFirstInflection,
            minLastInflection=minLastInflection,
            ceofThreshold=0.9,
            ceofDiffEpsilon=0.00001,
            rollingWinSize=rollingWinSize,
            fixedPointRate=fixedPointRate,
            numPotentialInflection=numPotentials,
            debugLevel=0,
        )
        max_cor_coef, max_reg_coef, cp = pw.doPieceWise(df, ctx)

        res = {
            'NS': len(cp)+1,
            'ceof': max_cor_coef,
        }
        for i in range(len(cp)):
            res["S{0}".format(i+1)] = cp[i]
        for i in range(len(max_reg_coef)):
            res["b{0}".format(i+1)] = max_reg_coef[i]
    elif method == AnalysisMethood.MAX:
        res = {
            'max': y.max()
        }
    else:
        print("unknown analysis method")

    return res


# main entry
debugSinglePoint = False


if __name__ == "__main__":
    if debugSinglePoint is True:  # for debug in single point
        # for debug sinle point
        x = np.array(list(range(1, 21)))
        y = np.array([
            1447, 1580, 2037, 1779.9266, 1398.0007, 1614.4379,
            1493.4379, 1580, 1613, 1728.7712, 1630.695, 1516.4379,
            1775.1046, 1434.4379, 1383.695, 1720.7784, 1664, 1578.9172,
            1711.4103, 1691])
        # analyzeSinglePoint(x, y, AnalysisMethood.OLS)
        # analyzeSinglePoint(x, y, AnalysisMethood.MANNKENDALL)
        analyzeSinglePoint(x, y, AnalysisMethood.PIECEWISE)
    else:
        parser = argparse.ArgumentParser(
                description="Analysis program for mod13q1 in geotiff format")
        parser.add_argument(
                "method",
                help="one option of [ LS, MANNKENDALL, PIECEWISE, MAX ]")
        parser.add_argument(
                "src",
                help="input geotiff file for analysis")
        parser.add_argument(
                "timeStart", type=int, help="start time")
        parser.add_argument("destDir",
                            help="output directory to store analysis results")
        parser.add_argument(
                "-d", "--debug", action="store_true", help="for debug")

        args = parser.parse_args()
        print("input arguments", args)

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
        elif args.method == "MANNKENDALL":
            method = AnalysisMethood.MANNKENDALL
        elif args.method == "PIECEWISE":
            method = AnalysisMethood.PIECEWISE
        elif args.method == "MAX":
            method = AnalysisMethood.MAX
        else:
            method = AnalysisMethood.UNKNOWN
        opts = {
                "method": method,
                "timeStart": args.timeStart,
                "debug": args.debug,
                }
        t1 = datetime.now()
        analyzeGrid(fInput, opts, outputDir, fOutputPrefix, method)
        t2 = datetime.now()
        print("time cost:", (t2-t1))