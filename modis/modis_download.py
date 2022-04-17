#!/usr/bin/env python3
import os
# import glob
import re
import shutil


def download(product_id, product_version, h, v, years, output, user, password):
    product = "{0}.{1}".format(product_id, product_version)
    remoteRoot = "https://e4ftl01.cr.usgs.gov/MOLT/{PP}/".format(PP=product)
    rpathPattern = "{REMOTE_ROOT}"
    lpathPattern = "{LOCAL_ROOT}/h{HH}v{VV}"

    # wget usage:
    # wget --http-user=zhujiang --http-password=1234 -r --level=2 -nd
    # -P /Users/hurricane/share/modis/MCD12Q1.006/h25v04 -np
    # -A "*.*201[2-4]*.h25v04.*.hdf,*.h25v04.*.jpg,*.h25v04.*.hdf.xml"
    # --reject-regex=".*\?.*" https://e4ftl01.cr.usgs.gov/MOTA/MCD12Q1.006/
    cmdPatten = (
            "wget --http-user={User} --http-password={Password} "
            "-r --level=2 -nd -P {LocalDir} -np -A \"{AcceptList}\" "
            "--reject-regex=\".*\\?.*\" {RemoteDir}"
            )

    if years == "*":
        accListPatterns = ",".join([
            "*.h{HH}v{VV}.*." + suffix
            for suffix in productSuffix(product_id)])
    else:
        accListPatterns = ",".join([
            "*.*" + years + "*.h{HH}v{VV}.*." + suffix
            for suffix in productSuffix(product_id)])

    if h != "*" and v != "*":
        localDir = lpathPattern.format(
                LOCAL_ROOT=output, HH=h, VV=v)
    else:
        localDir = lpathPattern.format(
                LOCAL_ROOT=output, HH="", VV="")

    acclist = accListPatterns.format(HH=h, VV=v)
    remoteDir = rpathPattern.format(REMOTE_ROOT=remoteRoot)
    cmd = cmdPatten.format(
            User=user,
            Password=password,
            LocalDir=localDir,
            AcceptList=acclist,
            RemoteDir=remoteDir)
    # print(cmd)
    os.system(cmd)


# helper functions
def rearrangeDirectories(output, h, v,  mode):
    lpathPattern = "{LOCAL_ROOT}/h{HH}v{VV}"
    if h != "*" and v != "*":
        hvDir = lpathPattern.format(
                LOCAL_ROOT=output, HH=h, VV=v)
    else:
        hvDir = lpathPattern.format(
                LOCAL_ROOT=output, HH="", VV="")

    for f in os.listdir(hvDir):
        fPath = os.path.join(hvDir, f)
        if os.path.isfile(fPath):
            m = re.search(r"(\d{4})\d{3}.(h\d+v\d+)", f)
            if m:
                yearDir = os.path.join(hvDir, m.group(1))
                if not os.path.exists(yearDir):
                    os.makedirs(yearDir)
                src = fPath
                dest = os.path.join(yearDir, f)
                shutil.move(src, dest)


def productSuffix(product_id):
    if product_id.startswith("MOD"):
        return ["hdf", "jpg", "hdf.xml"]
    else:
        print("invad product: ", product_id)
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
    # Requires a NASA Earthdata Login username and password.
    # To obtain a NASA Earthdata Login account, please visit
    # https://urs.earthdata.nasa.gov/users/new/.
    user = "freeforever"
    password = "zycgod781123"

    product_id = "MOD13Q1"
    product_version = "061"
    outputDir = "d:/glass/modis/{0}.{1}/".format(
            product_id, product_version)
    # or
    # outputDir = "Z:/share/modis/{0}.{1}/".format(product_id, product_version)

    # years pattern:
    # "2012 "for single year
    # "201[2-4]" represents 2012, 2013, 2014
    # "201* "for [2010 - 2019]
    # "*" for all years
    # years = "201[2-4]"
    years = "*"

    hvs = [
            # ("23", "04"),
            # ("23", "05"),
            ("25", "04")]
    # or download all scenes with ("*", "*")
    # hvs = [("*", "*")]

    # organize files by year after download
    orderByYear = True
    # --------------------------------------------
    for hv in hvs:
        (h, v) = hv
        print("downloading {0}.{1} h{2}v{3} ...".format(
            product_id, product_version, h, v))
        # download(
        #         product_id, product_version,
        #         h, v, years,
        #         outputDir,
        #         user, password)

        if orderByYear is True:
            rearrangeDirectories(outputDir, h, v, mode="BY-YEAR")
