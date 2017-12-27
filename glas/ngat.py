#!D:/Python27/python.exe
#coding=utf-8

import os
import sys

import numpy as np
# for walk around the bug that the directory of os.path.abspath(__file__) will change to home when import idl_python_bridge
thisfile__abspath = os.path.realpath(os.path.abspath(__file__))

"""Extract elevation and geoid data from GLAS altimetry products.
   Wrapper for NSIDC GLAS Altimetry elevation extractor Tool (NGAT)
"""
class ElevationExtractor(object):

    def __init__(self, arg):
        super(self.__class__, self).__init__()
        self.arg = arg

    def genAltimetryReaderInit(self, indir, outdir, subset):
        iniTemplateFile = "batch_read_altimetry_template.ini"
        iniFile = "batch_read_altimetry.ini"
        curPath = os.path.split(thisfile__abspath)[0]
        iniPath = os.path.join(curPath, iniFile)

        paras = []
        with open(os.path.join(curPath, iniTemplateFile)) as iniTempFo:
            paras = iniTempFo.readlines()

        if indir == "":
            indir = os.path.join(curPath, "data")
        if outdir == "":
            outdir = os.path.join(curPath, "step1")

        mkDirIfNotExist(outdir)

        infiles = self.genFileListInDir(indir)
        outfiles = infiles.replace(".DAT", ".txt")

        #print(infiles)
        #print(outfiles)

        strParas = "".join(paras)
        strParas = strParas.replace("$INDIR", indir)
        strParas = strParas.replace("$OUTDIR", outdir)
        strParas = strParas.replace("$SUBSET", subset)
        strParas = strParas.replace("$INFILES", infiles)
        strParas = strParas.replace("$OUTFILES", outfiles)

        with open(iniPath, "w+") as inifo:
            inifo.writelines(strParas)

        print("File %s is generated. " %iniPath)

    def genFileListInDir(self, path):
        items = os.listdir(path)

        newlist = []
        for fname in items:
            if fname.startswith("GLA") and fname.endswith(".DAT"):
                newlist.append(fname)
        return ';'.join(newlist)


"""
Base GLAS dataset processor class with common operations
"""
class GLASProcessorBase(object):
    def __init__(self, arg):
        self.arg = arg

        "outputContentFormat and outputHeader Variables should been overridden."
        self.outputHeader = ""
        self.outputContentFormat = ""

    """reads records(lines) from a single input file
    """
    def readFromInput(self, input):
        with open(input) as inputFile:
            data = inputFile.readlines()
        return data

    def writeToOutput(self, output, data, mode="w"):
        with open(output, mode) as outputFile:
            outputFile.writelines(data)

    """define the abstract processing function which should been overridden.
       result data instead raw data should been return.
    """
    def processSingleDataset(self, data, return_with_header=False):
        print("processing data: \n {}\n".format(data))
        return []

    def batchProcessDataset(self,inDir, outDir, outputHeader=False):
        mkDirIfNotExist(outDir)
        items = os.listdir(inDir)
        for fname in items:
            data = self.readFromInput(os.path.join(inDir, fname))
            result = self.processSingleDataset(data)
            if outputHeader == True:
                result.insert(0, self.outputHeader)
            self.writeToOutput(os.path.join(outDir, fname), result)


""" Elevation Correction Process include Saturation Correction
    and Converter of elevation from the TOPEX/Poseidon ellipsoid to the WGS-84 ellipsoid
    top_elev = elevation + i_SatElevCorr，elevation by saturation correction on TOPEX/Poseidon ellipsoid
    wgs84_elev = top_elev - i_deltaEllip
    ICESat_wgs84 = ICESat_topex(top_elev) - ICESat_geoid - Offset
    Icesat_wgs84_II is caculated by wgs2top tool (Ref: IDL Ellipsoid Conversion, See http://nsidc.org/data/icesat/tools.html)
"""
class ElevationCorrection(GLASProcessorBase):
    def __init__(self, arg):
        super(self.__class__, self).__init__(arg)
        self.arg = arg
        from ellipsoidwrapper import EllipsoidWrapper
        self.ew = EllipsoidWrapper()

        # self.outputHeader = "{:>9}\t{:>10}\t{:>12}\t{:>12}\t{:>12}\t{:>12}\t{:>12}\t{:>12}\t{:>14}\t{:>10}\t{:>16}\t{:>14}\t{:>8}\t{:>10}\t{:>18}\t{:>18}\t{:>18}\n".format(
        #     "RecNo", "Date", "Time", "Latitude","Wgs84_lat", "Longitude", "Elevation(m)", "Geoid(m)", "SatElevCorr(m)", "Gval_rcv",
        #     "UTCTime","DeltaEllip(m)","GmC", "Top_elev(m)", "wgs84_elve_I(m)","wgs84_elve_II(m)","wgs84_elve_III(m)"
        # )
        # self.outputContentFormat = "{:>9}\t{:>10}\t{:>12}\t{:>12}\t{:>12.6f}\t{:>12}\t{:>12}\t{:>12}\t{:>14}\t{:>10}\t{:>16}\t{:>14}\t{:>8}\t{:>10.3f}\t{:>18.3f}\t{:>18.3f}\t{:>18.3f}\n"

        self.outputHeader = "{:<9}\t{:<10}\t{:<12}\t{:<12}\t{:<12}\t{:<12}\t{:<12}\t{:<12}\t{:<14}\t{:<10}\t{:<16}\t{:<14}\t{:<8}\t{:<10}\t{:<18}\t{:<18}\t{:<18}\n".format(
            "RecNo", "Date", "Time", "Latitude","Wgs84_lat", "Longitude", "Elevation(m)", "Geoid(m)", "SatElevCorr(m)", "Gval_rcv",
            "UTCTime","DeltaEllip(m)","GmC", "Top_elev(m)", "wgs84_elve_I(m)","wgs84_elve_II(m)","wgs84_elve_III(m)"
        )
        self.outputContentFormat = "{:<9}\t{:<10}\t{:<12}\t{:<12}\t{:<12.6f}\t{:<12}\t{:<12}\t{:<12}\t{:<14}\t{:<10}\t{:<16}\t{:<14}\t{:<8}\t{:<10.3f}\t{:<18.3f}\t{:<18.3f}\t{:<18.3f}\n"

    """ Elevation Correction Process processing override GLASProcessorBase's method
        Saturation Correction:
            'top_elev = elevation + i_SatElevCorr'
        Caculate wgs84_elev using both formulas:
            'wgs84_elev = top_elev - i_deltaEllip'
            'ICESat_wgs84 = ICESat_topex(top_elev) - ICESat_geoid - Offset',
        and append to raw line.
    """
    def processSingleDataset(self, data, return_with_header=False):
        """ Columns format:
            0- Record Number -  1 record (40 samples)
            1- Date          -  MM/DD/YYYY
            2- Time          -  HH:MM:SS.sss
            3- Latitude      -  'i_lat' converted to degrees
            4- Longitude     -  'i_lon' converted to degrees
            5- elevation     -  the 'i_elev' field for the chosen product number, converted to meters
            6- geoid	  -  the 'i_gdHt' values, interpolated for each shot also
                             converted to meters

            7- i_SatElevCorr, - the 'i_SatElevCorr' field for Saturation Elevation Correction , converted to meters (I guess so)
            8- i_gval_rcv,    - the 'i_gval_rcv' field for Gain Value used for Received Pulse
            9- i_UTCTime,     - i_UTCTime in decimal seconds to 3 decimal places (i.e. having 1 millisecond precision)
           10- i_deltaEllip,  - i_deltaEllip whose value is Surface Elevation (T/P ellipsoid) minus Surface Elevation(WGS84 ellipsoid).
           11-i_GmC,          --the i_GmC field, the variable is defined as the difference in the transmit pulse gaussian fit and the centroid of the transmit pulse.
        """

        resultData = []
        recCnt = len(data)
        if recCnt ==0:
            return resultData

        offset = 0.7  # 0.7m
        top_lat_arr = np.zeros(recCnt)
        top_elev_arr = np.zeros(recCnt)

        # top_geoid_arr = np.zeros(recCnt)
        rec_no = 0
        tempData = []

        for line in data:
            items = line.split()
            top_elev = float(items[5]) + float(items[7])

            top_lat_arr[rec_no] = float(items[3])
            top_elev_arr[rec_no] = top_elev

            # top_geoid_arr[rec_no] = float(items[6])
            tempData.append(items)
            rec_no +=1

        # call top2wgs to transformation from topex to wgs84 ellipsoid
        wgs_lat_arr3, wgs_elev_arr3 = self.ew.top2wgs(top_lat_arr, top_elev_arr)

        # wgs_lat_arr3, wgs_geoid_arr3 = self.ew.top2wgs(top_lat_arr, top_geoid_arr)
        # for i in range(recCnt):
        #    print(top_geoid_arr[i], wgs_geoid_arr3[i] + 0.706 )

        rec_no = 0
        for items in tempData:
            items[1] = monDayYear2YearMonDay(items[1], "/")
            top_lat_arr[rec_no] = float(items[3])
            # top_elev = i_lat + i_SatElevCorr
            top_elev = float(items[5]) + float(items[7])
            top_elev_arr[rec_no] = top_elev
            # let offset be i_deltaEllip instead of 0.7m
            offset = float(items[10])

            wgs84_elev_1 = top_elev - float(items[10])
            icesat_geoid = float(items[6])
            icesat_wgs84_2 = top_elev - icesat_geoid - offset

            # ref: http://nsidc.org/data/icesat/geoid.html
            # ICESat/GLAS elevations above the ellipsoid (i_elev) are referenced to the TOPEX/Poseidon ellipsoid
            # Release-12 and -14 ICESat/GLAS geoid height data (i_gdHt) were referenced to the WGS-84 ellipsoid in a tide-free system.
            # So, the icesat_wgs84_3 ( Surface elevation with respect to the geoid) = wgs_elev - icesat_geoid
            icesat_wgs84_3 = wgs_elev_arr3[rec_no] -icesat_geoid
            newItem = self.outputContentFormat.format(
                items[0], items[1], items[2], items[3],wgs_lat_arr3[rec_no],
                items[4], items[5], items[6],items[7],
                items[8], items[9], items[10], items[11],
                top_elev,wgs84_elev_1,icesat_wgs84_2, icesat_wgs84_3
            )

            rec_no += 1
            resultData.append(newItem)

        return resultData

    """
    Batch Process Dataset override GLASProcessorBase's method
    """
    def batchProcessDataset(self,inDir, outDir, outputHeader=False):
        mkDirIfNotExist(outDir)
        items = os.listdir(inDir)

        conbinedFile = os.path.join(outDir, "conbined.txt")
        if outputHeader == True:
            conbinedHeader = [self.outputHeader]
            self.writeToOutput(conbinedFile, conbinedHeader)

        for fname in items:
            data = self.readFromInput(os.path.join(inDir, fname))
            result = self.processSingleDataset(data)

            self.writeToOutput(conbinedFile, result, "a")

            if outputHeader == True:
                result.insert(0, self.outputHeader)
            self.writeToOutput(os.path.join(outDir, fname), result)


def mkDirIfNotExist(path):
    if not os.path.exists(path):
        os.makedirs(path)
def monDayYear2YearMonDay(mdy, sep):
    arr = mdy.split(sep)
    ydm = "{year}{sep_ch}{mon}{sep_ch}{day}".format(year=arr[2], mon=arr[0], day=arr[1], sep_ch=sep)
    return ydm


if __name__ == "__main__":

    # default indir and outdir will be subdir of current dir if not setting.
    # sample with relative path
    # curDir = os.path.split(thisfile__abspath)[0]
    # glas_data_indir = os.path.join(curDir,"data")
    # exactDem_outdir = os.path.join(curDir,"step1")
    # wgs84Dem_outdir = os.path.join(curDir, "step2")
    # subset = "[40, 99, 43, 102]"

    # sample with absolute path
    # glas_data_indir = "E:/zhangyc/glas/data"
    # exactDem_outdir = "E:/zhangyc/glas/step1"
    # topDem_outdir = "E:/zhangyc/glas/step2"
    # wgs84Dem_outdir = "E:/zhangyc/glas/step3"


    # add by zhangyc
    glas_data_indir = "C:/Users/Dell/Downloads/ICESat"
    exactDem_outdir = "E:/Data/ICESat/step1"
    wgs84Dem_outdir = "E:/Data/ICESat/step2"
    subset = "[37, 93, 43, 107]"

    if len(sys.argv) < 2 or sys.argv[1] == "ElevationExtractor":
        eleExtractor = ElevationExtractor("")
        eleExtractor.genAltimetryReaderInit(glas_data_indir, exactDem_outdir, subset)

    elif sys.argv[1] == "ElevationCorrection":
        ec = ElevationCorrection("")
        ec.batchProcessDataset(exactDem_outdir, wgs84Dem_outdir, True)

else:
    print("loading ngat module")
