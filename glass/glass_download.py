#!/usr/bin/env python3
import os
# import glob


def download_glass(product, h, v, years, output):
    # lf = "url.txt"
    remoteRoot = "http://www.glass.umd.edu/{PP}/MODIS/1km".format(PP=product)
    rpathPattern = "{REMOTE_ROOT}/{YYYY}/"
    lpathPattern = "{LOCAL_ROOT}/h{HH}v{VV}/{YYYY}"

    # wget -r -nd -P /Users/hurricane/share/glass/ET/h25v04/2013 --no-parent
    # -A '*.h25v04.*.hdf,*.h25v04.*.hdf.jpg,*.h25v04.*.hdf.xml'
    # --reject-regex '(.*)\?(.*)' http://www.glass.umd.edu/ET/MODIS/1km/2013/
    cmdPatten = (
            "wget -r -nd -P {LocalDir} -np -A '{AcceptList}' "
            "--reject-regex \'(.*)\\?(.*)\' {RemoteDir}"
            )

    accListPatterns = ",".join([
            "*.h{HH}v{VV}.*." + suffix for suffix in productSuffix(product)])

    # print(accListPatterns)
    # print(years)
    for year in range(years["start"], years["end"]):
        # for d in range(46):
        # day = "{:>03d}".format(d*8 + 1)
        localDir = lpathPattern.format(
                LOCAL_ROOT=output, HH=h, VV=v,  YYYY=year)
        acclist = accListPatterns.format(HH=h, VV=v)
        remoteDir = rpathPattern.format(
                REMOTE_ROOT=remoteRoot, YYYY=year)
        cmd = cmdPatten.format(
                LocalDir=localDir,
                AcceptList=acclist,
                RemoteDir=remoteDir)
        print(cmd)
        os.system(cmd)


# helper functions
# def productPrefix(product):
#     if product == "LAI":
#         return "GLASS01E01.V50"
#     elif product == "ET":
#         return "GLASS11A01.V42"
#     else:
#         print("invad product")
#         return ""


def productSuffix(product):
    if product == "LAI":
        return ["hdf", "LAI.jpg", "hdf.xml"]
    elif product == "ET":
        return ["hdf", "hdf.jpg", "hdf.xml"]
    else:
        print("invad product")
        return []


# def producedYD(product, year, ddd):
#     if product == "LAI":
#         return 2020323
#     elif product == "ET":
#         d = year * 1000 + ddd
#         if d <= 2007033:
#             return 2019311
#         else:
#             return 2019312
#     else:
#         print("invad product")
#         return 0


# def removeInvalidFiles(rootDir, pattern="*.hdf"):
#     files = []
#     for root, dirnames, filenames in os.walk(rootDir):
#         # print(root, dirnames, filenames)
#         # print(root + pattern)
#         files.extend(glob.glob(root + "/" + pattern))

#     for fp in files:
#         fs = os.stat(fp).st_size / 1024
#         if fs <= 200:
#             print(fp, fs)
#             os.remove(fp)


if __name__ == "__main__":
    # h = "23"
    # v = "04"

    # product = "LAI"
    # or
    product = "ET"
    outputDir = "/Users/hurricane/share/glass/{0}".format(
            product)
    # data in [start, end), for example:
    # years = [start=2013, end=2014) presents data in year 2013
    years = dict(start=2000, end=2019)

    hvs = [
            ("23", "04"),
            ("23", "05"),
            ("25", "04")]
    for hv in hvs:
        (h, v) = hv
        download_glass(product, h, v, years, outputDir)
