#!/usr/bin/env python3
import os


def download_glass(product, h, v):
    lf = "url.txt"
    root = "http://www.glass.umd.edu/{PP}/MODIS/1km/".format(PP=product)
    prefix = productPrefix(product)
    filePattern = "{PREFIX}.A{YYYY}{DDD}.h{HH}v{VV}.{PD}.{SS}"
    pathPattern = "{ROOT}/{YYYY}/{DDD}/{FFF}\n"
    outRoot = "/Users/hurricane/workspace/igsnrr/data/glass/{PP}".format(
            PP=product)

    lines = []
    suffix = productSuffix(product)

    for year in range(2000, 2019):
        for d in range(46):
            day = "{:>03d}".format(d*8 + 1)
            pd = producedYD(product, year, int(day))
            for ss in suffix:
                f = filePattern.format(
                        PREFIX=prefix,
                        YYYY=year, DDD=day,
                        HH=h, VV=v,
                        PD=pd, SS=ss)
                fp = pathPattern.format(ROOT=root, YYYY=year, DDD=day, FFF=f)
                lines.append(fp)

    outDir = "{ROOT}/h{HH}v{VV}".format(ROOT=outRoot, HH=h, VV=v)
    if not os.path.exists(outDir):
        os.makedirs(outDir)

    lf = outDir + "/" + lf
    with open(lf, "w") as fo:
        fo.writelines(lines)

    getDataWithWget = "wget -i {0} -P {1}".format(lf, outDir)
    # print(getDataWithWget)
    os.system(getDataWithWget)


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


if __name__ == "__main__":
    h = "25"
    v = "04"

    # download_glass("ET", h, v)
    download_glass("LAI", h, v)
