#!/usr/bin/env python3
import os
import glob


def download_glass(product, h, v, output):
    # lf = "url.txt"
    root = "http://www.glass.umd.edu/{PP}/MODIS/1km".format(PP=product)
    prefix = productPrefix(product)
    filePattern = "{PREFIX}.A{YYYY}{DDD}.h{HH}v{VV}.{PD}.{SS}"
    pathPattern = "{ROOT}/{YYYY}/{DDD}/{FFF}"

    lines = []
    suffix = productSuffix(product)

    for year in range(2005, 2019):
        for d in range(46):
            day = "{:>03d}".format(d*8 + 1)
            pd = producedYD(product, year, int(day))
            for ss in suffix:
                f = filePattern.format(
                        PREFIX=prefix,
                        YYYY=year, DDD=day,
                        HH=h, VV=v,
                        PD=pd, SS=ss)
                rfp = pathPattern.format(ROOT=root, YYYY=year, DDD=day, FFF=f)
                lfp = pathPattern.format(
                        ROOT=output, YYYY=year, DDD=day, FFF=f)
                # lines.append("{0} -P {1}".format(rfp, lfp))
                lines.append("{0}\n".format(rfp))

                if not os.path.exists(os.path.dirname(lfp)):
                    os.makedirs(os.path.dirname(lfp))

                cmd = "wget -c {0} -O {1}".format(rfp, lfp)
                os.system(cmd)

    # outDir = "{ROOT}/h{HH}v{VV}".format(ROOT=outRoot, HH=h, VV=v)
    # outDir = "{ROOT}/h{HH}v{VV}".format(ROOT=outRoot, HH=h, VV=v)
    # if not os.path.exists(output):
    #     os.makedirs(output)

    # lf = os.path.join(output, lf)
    # with open(lf, "w") as fo:
    #     fo.writelines(lines)

    # getDataWithWget = "wget -i {0}".format(lf)
    # print(getDataWithWget)
    # os.system(getDataWithWget)


# helper functions
def productPrefix(product):
    if product == "LAI":
        return "GLASS01E01.V50"
    elif product == "ET":
        return "GLASS11A01.V42"
    else:
        print("invad product")
        return ""


def productSuffix(product):
    if product == "LAI":
        return ["hdf", "LAI.jpg", "hdf.xml"]
    elif product == "ET":
        return ["hdf", "hdf.jpg", "hdf.xml"]
    else:
        print("invad product")
        return []


def producedYD(product, year, ddd):
    if product == "LAI":
        return 2020323
    elif product == "ET":
        d = year * 1000 + ddd
        if d <= 2007033:
            return 2019311
        else:
            return 2019312
    else:
        print("invad product")
        return 0


def removeInvalidFiles(rootDir, pattern="*.hdf"):
    files = []
    for root, dirnames, filenames in os.walk(rootDir):
        # print(root, dirnames, filenames)
        # print(root + pattern)
        files.extend(glob.glob(root + "/" + pattern))

    for fp in files:
        fs = os.stat(fp).st_size / 1024
        if fs <= 200:
            print(fp, fs)
            os.remove(fp)


if __name__ == "__main__":
    h = "25"
    v = "05"
    product = "LAI"
    # or
    # product = "ET"
    outputDir = "/Users/hurricane/share/glass/{0}".format(
            product)

    # download_glass(product, h, v, outputDir)
    removeInvalidFiles(outputDir, "*.hdf")
