# -*- coding: utf-8 -*-
import os
import argparse
import rasterio


def joinFiles(inputdir, outputDir, fprefix):
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    files = []
    f_list = sorted(os.listdir(inputDir))

    print("valid files:")
    for f in f_list:
        if os.path.splitext(f)[1] == '.tif':
            print(f)
            files.append(f)

    fInput = os.path.join(inputDir, files[0])
    profile = None
    descriptions = None
    with rasterio.open(fInput) as dt_in:
        profile = dt_in.profile.copy()
        # defaults= {'blockxsize': 256, 'blockysize': 256, 'compress': 'lzw',
        # 'driver': 'GTiff', 'dtype': 'uint8', 'interleave': 'band',
        # 'nodata': 0, 'tiled': True}
        profile.update({
                'count': len(files),
                'dtype': 'float32',
                'height': dt_in.height,
                'width': dt_in.width,
                'blockxsize': 256,
                'blockysize': 256,
                'compress': 'lzw',
                'interleave': 'band',
                # 'tiled': True
                })
        # print("profile", profile)
        # print("descriptions", dt_in.descriptions)
        descriptions = dt_in.descriptions

    for bandId, bandname in enumerate(descriptions):
        if bandname is None:
            bandname = "band{0}".format(bandId + 1)

        print("\njoin band {0} {1} ...".format(bandId+1, bandname))
        print(fprefix, bandname)
        fName = fprefix + "-" + bandname + ".tif"
        fOutput = os.path.join(outputDir, fName)
        print("write to {0} ...".format(fOutput))

        # with rasterio.open(fOutput, 'w', **profile) as dt_out:
        with rasterio.open(fOutput, 'w', **profile, BIGTIFF='YES') as dt_out:
            year_index = 1
            descs = []
            
            part_mask_arr = []
            for fo in files:
                fInput = os.path.join(inputDir, fo)
                with rasterio.open(fInput) as dt_in:
                    ndvi_arr = dt_in.read(bandId + 1)
                    dt_out.write_band(year_index, ndvi_arr)
                    desc = fo.replace(".tif", "")
                    print("writing band: ", desc)
                    descs.append(desc)
                    year_index += 1

                    part_mask = dt_in.read_masks(bandId + 1)
                    part_mask_arr.append(part_mask)
            
            mask = part_mask_arr[0]
            for i in range(1, len(part_mask_arr)):
                mask = mask & part_mask_arr[i]
            dt_out.descriptions = descs
            dt_out.write_mask(mask)
            # print("descriptions: ", dt_out.descriptions)
        
        with rasterio.open(fOutput, 'r') as dt:
            print("descriptions: ", dt.descriptions)
            print("Profile:", dt.profile)



if __name__ == "__main__":
    workspace = "/Users/hurricane/workspace/igsnrr/data/MOD13Q1/"
    inputDir = os.path.join(workspace, "MOD13Q1-MEDIAN-XJ")
    outputDir = os.path.join(workspace, "MOD13Q1-MEDIAN-XJ-join")
    prefix = "MOD13Q1-MEDIAN-XJ-join"

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
