# !/usr/bin/python
# -*- coding: utf-8 -*-
# COPYRIGHT 2016 igsnrr
#
# MORE INFO ...
# email:

import os
import shutil
import time
from datetime import date
from datetime import timedelta, datetime
import pandas as pd

from igsnrr.base.toolbase import ToolBase


class Surf4HoursTool(ToolBase):
    """The tool is designed to convert surf files orgarnized by month into
    files by station IDs and statisics for daily and monthly."""
    def __init__(self):
        ToolBase.__init__(self, "Surf4HoursTool",
                          "The Surf4Hours Tool convert surf files organized \
                          by day into files organized by station. and \
                          statisics for daily and monthly.")
        self._version = "surf4hourstool.py 0.0.1"

    def defineArgumentParser(self, parser):
        parser.add_argument("source", action="store",
                            help="root dir for source files")
        parser.add_argument("target", action="store",
                            help="root dir for target files")

    def run(self, args):
        srcRoot = args.source
        targetRoot = args.target
        print(srcRoot, "-->", targetRoot)

        bystationDir = os.path.join(targetRoot, "bystation")
        dailyDir = os.path.join(targetRoot, "daily")
        monthlyDir = os.path.join(targetRoot, "monthly")
        self.batchConvert(srcRoot, bystationDir)
        self.statisticsDaily(bystationDir, dailyDir)
        self.statisticsMonthly(dailyDir, monthlyDir)

    def batchConvert(self, srcPathRoot, targetPathRoot):
        if (os.path.exists(targetPathRoot)
                and len(os.listdir(targetPathRoot)) > 0):
            print("\nThe dir of {0} is not empty and will been overrided."
                  .format(targetPathRoot))
            # ans = input()
            # if ans is "" or ans.lower() == "y" or ans.lower() == "yes":
            shutil.rmtree(targetPathRoot, True)
            time.sleep(1)
            # else:
            #     self._logger.info("Failed: {0} has existed and can't been \
            #                       overrided ".format(targetPathRoot))
            #     return
        if not os.path.exists(targetPathRoot):
            os.makedirs(targetPathRoot)

        filelist = sorted(os.listdir(srcPathRoot))

        for item in filelist:
            srcPath = os.path.join(srcPathRoot, item)
            print(srcPath)
            self.convert(srcPath, targetPathRoot)

        self.insertHeader(targetPathRoot)

    def convert(self, srcPath, targetRoot):
        if not os.path.exists(srcPath):
            self._loggej.info("Failed: {0} does't existe".format(srcPath))

        recs = []
        with open(srcPath) as f:
            recs = f.readlines()
            recs = recs[2:]
        f.close()

        group = {}
        strfmt = ("{0:>8}{1:>6d}{2:0>2d}{3:0>2d}{4:0>2d}"
                  "{1:>6d}{2:>4d}{3:>4d}{4:>4d}"
                  "{5:>12.1f}{6:>12.1f}{7:>12.1f}\n")
        for rec in recs:
            items = rec.split()
            if items[0] not in group:
                group[items[0]] = []

            rec = strfmt.format(items[0], int(items[1]), int(items[2]),
                                int(items[3]), int(items[4]), float(items[5]),
                                float(items[6]), float(items[7]))
            group[items[0]].append(rec)

        for k, v in group.items():
            target = os.path.join(targetRoot, k)
            # print(v)
            with open(target, 'a') as fo:
                fo.writelines(v)
            fo.close()

    def insertHeader(self, parentDir):
        header = ("{0:>8}{1:>12}{2:>6}{3:>4}{4:>4}{5:>4}"
                  "{6:>12}{7:>12}{8:>12}\n").format("SID", "DATETIME", "YEAR",
                                                    "MON", "DAY", "HR",
                                                    "PRES", "TEMP", "PREC")
        filelist = sorted(os.listdir(parentDir))
        for item in filelist:
            with open(os.path.join(parentDir, item), 'r+') as fo:
                recs = fo.readlines()
                fo.seek(0)
                fo.write(header)
                fo.writelines(recs)
                fo.flush()
            fo.close()

    def statisticsDaily(self, srcPathRoot, targetPathRoot):
        if (os.path.exists(targetPathRoot)
                and len(os.listdir(targetPathRoot)) > 0):
            print("\nThe dir of {0} is not empty and will been overrided."
                  .format(targetPathRoot))
        if not os.path.exists(targetPathRoot):
            os.makedirs(targetPathRoot)

        filelist = os.listdir(srcPathRoot)
        for item in filelist:
            srcPath = os.path.join(srcPathRoot, item)
            targetPath = os.path.join(targetPathRoot, item)
            self.stasticsDailySingleStatation(item, srcPath, targetPath)

    def stasticsDailySingleStatation(self, sid, srcPath, targetPath):
        print("processing {0}".format(srcPath))
        db = pd.read_table(srcPath, skip_blank_lines=True,
                           delim_whitespace=True, index_col="DATETIME")
        result = []
        # todo: do config the range of loop

        year = 2010
        endDay = date(2020, 1, 1)
        curDay = date(year, 1, 1)
        while(curDay < endDay):
            recs = self.queryData(db, curDay, 8)
            if not recs.empty:
                day_rec = self.calcDaily(sid, curDay, recs)
                if day_rec is not None:
                    result.append(day_rec)
            curDay = curDay + timedelta(days=1)

        header = ("{:>8}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}"
                  "{:>10}{:>10}{:>10}\n") .format("SID", "DATE", "AVG_PRES",
                                                  "MAX_PRES", "MIN_PRES",
                                                  "AVG+TEMP", "MAX_TEMP",
                                                  "MIN_TEMP", "PREC20-20",
                                                  "PREC20-08", "PREC08-20")
        with open(targetPath, 'w') as fo:
            fo.write(header)
            fo.writelines(result)
        fo.close()

    def queryData(self, db, dt, df_hours=4):
        whf = datetime(dt.year, dt.month, dt.day, 0, 0, 0) \
            - timedelta(hours=df_hours)
        wht = whf + timedelta(hours=24)
        cond = "{0} < DATETIME <= {1}".format(whf.strftime("%Y%m%d%H"),
                                              wht.strftime("%Y%m%d%H"))
        recs = db.query(cond)
        return recs

    def calcDaily(self, sid, dt, hours24):
        """
        http://www.szmb.gov.cn/quf/2009/08/2017101815192310488.pdf
        """
        if (len(hours24) > 24):

                self._logger.error(("{1}-{2:0>2d}-{3:0>2d},"
                                    "Station {0} has more than 24 records on")
                                   .format(sid, dt.year, dt.month, dt.day))

        else:
            # statistics pressure
            valid_pressure = hours24.query("1200 > PRES > 800")
            # print(valid_pressure)
            if len(valid_pressure) == 24:
                # ok for 24 hours
                avg_pres = valid_pressure["PRES"].mean()
                max_pres = valid_pressure["PRES"].max()
                min_pres = valid_pressure["PRES"].min()
            else:
                valid_pressure = hours24.query(("1200> PRES > 600"
                                               "& HR in [2, 8, 14, 20]"))
                if len(valid_pressure) == 4:
                    avg_pres = valid_pressure["PRES"].mean()
                    max_pres = valid_pressure["PRES"].max()
                    min_pres = valid_pressure["PRES"].min()
                else:
                    avg_pres = 999999
                    max_pres = 999999
                    min_pres = 999999
                    self._logger.error(("{1}-{2:0>2d}-{3:0>2d},"
                                        "Station {0} miss pressure at"
                                        "[02, 08, 14, 20]")
                                       .format(sid, dt.year, dt.month, dt.day))

            # statistics temperature
            valid_temperature = hours24.query("60 > TEMP > -60")
            # print(valid_temperature)
            if len(valid_temperature) == 24:
                # ok for 24 hours
                avg_temp = valid_temperature["TEMP"].mean()
                max_temp = valid_temperature["TEMP"].max()
                min_temp = valid_temperature["TEMP"].min()
            else:
                valid_temperature = hours24.query("60> TEMP > -60 \
                                               & HR in [2, 8, 14, 20]")
                if len(valid_temperature) == 4:
                    avg_temp = valid_temperature["TEMP"].mean()
                    max_temp = valid_temperature["TEMP"].max()
                    min_temp = valid_temperature["TEMP"].min()
                else:
                    avg_temp = 999999
                    max_temp = 999999
                    min_temp = 999999
                    self._logger.error(("{1}-{2:0>2d}-{3:0>2d},"
                                        "Station {0} miss temperature at"
                                        "[02, 08, 14, 20]")
                                       .format(sid, dt.year, dt.month, dt.day))

            # statistics precipation
            valid_prec = hours24.query("200 > PREC >= 0")
            if len(valid_prec) != 24:
                prec24 = 999999
            else:
                prec24 = valid_prec["PREC"].sum()
            am_prec = valid_prec.query("HR <=8 | HR>20")
            pm_prec = valid_prec.query("8 <  HR <= 20")
            if len(am_prec) != 12:
                prec12_am = 999999
            else:
                prec12_am = am_prec["PREC"].sum()
            if len(pm_prec) != 12:
                prec12_pm = 999999
            else:
                prec12_pm = pm_prec["PREC"].sum()

            # print("prec: ", prec24, prec12_am, prec12_pm, "\n")

            rec = ("{:>8}{:>10}{:>10.1f}{:>10.1f}{:>10.1f}"
                   "{:>10.1f}{:>10.1f}{:>10.1f}"
                   "{:>10.1f}{:>10.1f}{:>10.1f}\n") \
                .format(sid, dt.strftime("%Y%m%d"),
                        avg_pres, max_pres, min_pres,
                        avg_temp, max_temp, min_temp,
                        prec24, prec12_am, prec12_pm)
            return rec

    def statisticsMonthly(self, srcPathRoot, targetPathRoot):
        pass


if __name__ == "__main__":
    # testing code
    # import sys
    # print(sys.argv)
    tool = Surf4HoursTool()
    import argparse
    from ..base.logger import Logger
    parser = argparse.ArgumentParser(prog="python.exe3 -m surf4hourstool",
                                     description="Surf4HoursTool Usage Guide",
                                     prefix_chars="-+")

    parser.add_argument("--version",
                        action="version", version="%(prog)s 0.0.1")

    tool.defineArgumentParser(parser)
    args = parser.parse_args()
    print(args)

    logger = Logger("./log/d2s.log")
    tool.attachLogger(logger)

    srcRoot = args.source
    targetRoot = args.target

    readme = srcRoot + "/readme.txt"
    if os.path.exists(readme):
        os.remove(readme)
    tool.run(args)

else:
    print("loading day2stationtool module")
