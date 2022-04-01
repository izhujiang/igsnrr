# -*- coding: utf-8 -*-
import os
import numpy as np
import rasterio
from enum import Enum
import argparse
import json
from datetime import datetime
import math
import multiprocessing as mp


class AnalysisMethood(Enum):
    OLS = 1,
    MANNKENDALL = 2,
    PIECEWISE = 4,
    MAX = 8,
    UNKNOWN = 256


# calc whole grid
def analyzeGrid(fInput, opts, outputDir, fOutputPrefix):
    # runMode = "multipleprocess"
    runMode = "singleprocess"
    with rasterio.open(fInput) as dt_in:
        profile = dt_in.profile.copy()
        # print(profile)

        width = profile['width']
        height = profile['height']
        cpu_num = int(mp.cpu_count())
        # cpu_num = 4
        step = math.ceil(height / cpu_num)

        if runMode == "singleprocess":
            print("running single process mode ... ")
            # TODO: change back to 0 range from 0
            for i in range(2, cpu_num):
                line_start = i * step
                line_end = min(line_start + step, height)
                chunk_opts = opts.copy()
                chunk_opts["line_start"] = line_start
                chunk_opts["line_end"] = line_end
                analyzeChunk(
                    "{:03d}".format(i+1), fInput, chunk_opts, outputDir,fOutputPrefix)
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
                        fOutputPrefix)
                )
            pool.close()
            pool.join()
        
        collectParts(profile, outputDir)

# combine parts into whole files
def collectParts(profile, outputDir):
    width = profile['width']
    height = profile['height']
    for root, dirs, _ in os.walk(outputDir, topdown=False):
        for name in dirs:
            cur_dir = os.path.join(root, name)
            part_arr = []
            part_mask_arr = []
            for part_file in sorted(os.listdir(cur_dir)):
                with rasterio.open(
                        os.path.join(cur_dir, part_file)) as partfile_in:
                    part_data = partfile_in.read(1)
                    part_arr.append(part_data)

                    part_mask = partfile_in.read_masks(1)
                    part_mask_arr.append(part_mask)

            # print(part_arr[0].shape, part_arr[3].shape)
            data = np.vstack(tuple(part_arr))
            mask = np.vstack(tuple(part_mask_arr))

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
                dt_out.write_mask(mask)


def analyzeChunk(chunkId, fInput, opts, outputDir, fOutputPrefix):
    '''
    analyzeChunk
    '''
    profile = None
    debug_infos = []

    method = opts["method"]
    analyzeSinglePoint = defaultAnalyzeSinglePoint
    if method == AnalysisMethood.OLS:
        import ols
        initResultStorage = ols.initResultStorage
        analyzeSinglePoint = ols.analyzeSinglePoint
    elif method == AnalysisMethood.MANNKENDALL:
        import mann_kendall as md
        initResultStorage = md.initResultStorage
        analyzeSinglePoint = md.analyzeSinglePoint
    elif method == AnalysisMethood.PIECEWISE:
        import pw
        initResultStorage = pw.initResultStorage
        analyzeSinglePoint = pw.analyzeSinglePoint
    elif method == AnalysisMethood.MAX:
        import max
        initResultStorage = max.initResultStorage
        analyzeSinglePoint = max.analyzeSinglePoint
    else:
        pass

    print("processing ", chunkId, opts)

    with rasterio.open(fInput) as dt_in:
        print("reading: ", fInput)
        profile = dt_in.profile.copy()
        # window = Window(col_off, row_off, width, height)
        width = profile["width"]
        height = opts["line_end"] - opts["line_start"]
        chunk_win = rasterio.windows.Window(
            0, opts["line_start"], width, height)
        ndvi_arr = dt_in.read(window=chunk_win, masked=True)
        msks = dt_in.read_masks(window=chunk_win)

        zlen, height, width = ndvi_arr.shape

        targetMask = msks[0, :, :]
        for i in range(1, zlen):
            targetMask = targetMask & msks[i, :, :]

        t = np.arange(opts["timeStart"], opts["timeStart"] + zlen)

        # fill the buf for storing analysis result
        bands_data, bands_desc = initResultStorage((height, width), dt_in.nodata)
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
            # if i % 40 == 0:
            #     print(
            #         "processing line : {0} at {1}".format(
            #             i + opts["line_start"], datetime.now()))

            for j in range(0, width):
                # if j % 100 == 0:
                #     print(
                #         "processing column : {0} at {1}".format(
                #             j, datetime.now()))

                y = ndvi_arr[:, i, j]
                # if not np.isnan(np.min(y)):
                if targetMask[i, j] == 0 or np.any(np.isnan(y)):
                    # print("targetMask[i, j]", targetMask[i,j])
                    for (k, vArray) in bands_data.items():
                        # vArray[i, j] = np.nan
                        # vArray[i, j] = dt_in.nodata
                        vArray[i, j] = -9999
                else:
                    # print("targetMask[i, j]", targetMask[i,j])
                    # print("values in i,j ", i, j, x, y)
                    resInPnt = analyzeSinglePoint(t, y)
                    for k in resInPnt:
                        bands_data[k][i, j] = resInPnt[k]
                    # for (k, vArray) in  bands_data.items():
                    #     vArray[i, j] = resInPnt[k]
                    if opts["debug"]:
                        debug_infos.append({
                            'loc_i': i, 'loc_j': j,
                            'v': y.tolist(), 'ana': resInPnt})

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
            # print(dt_in.nodata)
            dt_out.nodata = -9999
            dt_out.write_band(layerIndex, vArray)
            # dt_out.write_mask(targetMask)
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

def defaultInitResultStorage():
    print("default init result storage: do nothing")
    return {}

def defaultAnalyzeSinglePoint(x, y):
    print("default analysis for single point: do nothing")


# main entry
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analysis program for mod13q1 in geotiff format")
    parser.add_argument(
        "method",
        help="one option of [ OLS, MANNKENDALL, PIECEWISE, MAX ]")
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
    analyzeGrid(fInput, opts, outputDir, fOutputPrefix)
    t2 = datetime.now()
    print("time cost:", (t2-t1))