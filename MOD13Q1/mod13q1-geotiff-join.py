# -*- coding: utf-8 -*-
import os
import argparse
import rasterio


def joinFiles(inputdir, outputDir, fprefix):
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    files = sorted(os.listdir(inputDir))

    fInput = os.path.join(inputDir, files[0])
    profile = None
    descriptions = None
    with rasterio.open(fInput) as dt_in:
        profile = dt_in.profile.copy()
        profile.update({
                'count': len(files),
                'dtype': 'float32',
                'height': dt_in.height,
                'width': dt_in.width
                })
        # print("profile", profile)
        # print("descriptions", dt_in.descriptions)
        descriptions = dt_in.descriptions

    for bandId, bandname in enumerate(descriptions):
        print("\njoin band {0} {1} ...".format(bandId+1, bandname))
        fName = outputFilePrefix + "-" + bandname + ".tif"
        fOutput = os.path.join(outputDir, fName)
        print("write to {0} ...".format(fOutput))

        with rasterio.open(fOutput, 'w', **profile) as dt_out:
            year_index = 1
            for fo in files:
                fInput = os.path.join(inputDir, fo)
                print(fInput)
                with rasterio.open(fInput) as dt_in:
                    ndvi_arr = dt_in.read(bandId + 1)
                    dt_out.write_band(year_index, ndvi_arr)
                    year_index += 1


if __name__ == "__main__":
    workspace = "/Users/jiangzhu/workspace/igsnrr/data/MOD13Q1/"
    inputDir = os.path.join(workspace, "MOD13Q1-MEDIAN-XJ")
    outputDir = os.path.join(workspace, "MOD13Q1-MEDIAN-XJ-join")
    outputFilePrefix = "MOD13Q1-MEDIAN-XJ-join"

    parser = argparse.ArgumentParser(
            description="Join multiple tiff into serial files")
    parser.add_argument(
            "srcDir",
            help="input directory for geotiff files ")
    parser.add_argument(
            "destDir",
            help="output directory to store serial files")
    parser.add_argument(
            "prefix",
            help="prefix for serial files")

    args = parser.parse_args()
    print("input arguments: ", args)

    inputDir = args.srcDir
    outputDir = args.destDir
    prefix = args.prefix
    joinFiles(inputDir, outputDir, prefix)