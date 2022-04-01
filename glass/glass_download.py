#!/usr/bin/env python3
import os
# import glob
import re
import shutil


# download ET or LAI data to local storage
# parameters:
# product: ET or LAI
# h, v : 24 05
# year : 2000 -2021
# output: local directory for storing data
# result: output/h{dd}v{dd}/YYYY or output/YYYY
def download_glass(product, h, v, year, output):
    # lf = "url.txt"
    remoteRoot = "http://www.glass.umd.edu/{PP}/MODIS/1km".format(PP=product)
    rpathPattern = "{REMOTE_ROOT}/{YYYY}/"

    # wget usage:
    # wget -r -nd -P /Users/hurricane/share/glass/ET/h25v04/2013 --no-parent
    # -A '*.h25v04.*.hdf,*.h25v04.*.hdf.jpg,*.h25v04.*.hdf.xml'
    # --reject-regex=".*\?.*" http://www.glass.umd.edu/ET/MODIS/1km/2013/
    cmdPatten = (
            "wget -r -nd -P {LocalDir} -np -A \"{AcceptList}\" "
            "--reject-regex=\".*\\?.*\" {RemoteDir}"
            )

    accListPatterns = ",".join([
            "*.h{HH}v{VV}.*." + suffix for suffix in productSuffix(product)])

    if h != "*" and v != "*":
        lpathPattern = "{LOCAL_ROOT}/h{HH}v{VV}/{YYYY}"
        localDir = lpathPattern.format(
                LOCAL_ROOT=output, HH=h, VV=v,  YYYY=year)
    else:
        lpathPattern = "{LOCAL_ROOT}/{YYYY}"
        localDir = lpathPattern.format(
                LOCAL_ROOT=output, YYYY=year)

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
def rearrangeDirectories(rootDir, year, hv):
    if hv != "*":
        return
    # hvDir = os.path.join(rootDir, "hv")
    hvDir = rootDir
    yPath = os.path.join(hvDir, year)
    if os.path.isdir(yPath):
        for f in os.listdir(yPath):
            m = re.search(r"h\d+v\d+", f)
            if m:
                match_hv = m.group(0)
                hvPath = os.path.join(yPath, match_hv)
                if not os.path.exists(hvPath):
                    os.makedirs(hvPath)
                src = os.path.join(yPath, f)
                dest = os.path.join(hvPath, f)
                shutil.move(src, dest)
                print(match_hv, hvPath)


def productSuffix(product):
    if product == "LAI":
        return ["hdf", "LAI.jpg", "hdf.xml"]
    elif product == "ET":
        return ["hdf", "hdf.jpg", "hdf.xml"]
    else:
        print("invad product")
        return []


if __name__ == "__main__":
    # --!!! Import  ----------------------
    # make sure: wget's version >= 1.20 and --reject-regex option
    # using (wget -V) and (wget --help) commands
    # -A,  --accept=LIST           comma-separated list of accepted extensions
    # -R,  --reject=LIST           comma-separated list of rejected extensions
    #  --accept-regex=REGEX        regex matching accepted URLs
    #  --reject-regex=REGEX        regex matching rejected URL
    # DOWNLOAD wget for window from https://eternallybored.org/misc/wget/
    # NOT http://gnuwin32.sourceforge.net/packages/wget.htm , version 1.11.4
    # -------------------------------------
    # Input Parameters:

    # product = "LAI"
    # or
    product = "ET"
    outputDir = "/Users/hurricane/share/glass/{0}".format(
            product)
    # or
    # outputDir = "Z:/share/glass/ET2/"

    # data in [start, end), for example:
    # years = [start=2013, end=2014) presents data in year 2013
    years = range(2017, 2019)

    hvs = [
            # ("23", "04"),
            # ("23", "05"),
            ("25", "04")]
    # or download all scenes with ("*", "*")
    hvs = [("*", "*")]

    # --------------------------------------------
    for year in years:
        for hv in hvs:
            (h, v) = hv
            download_glass(product, h, v, year, outputDir)

            if h == "*" and v == "*":
                rearrangeDirectories(outputDir, str(year), "*")
