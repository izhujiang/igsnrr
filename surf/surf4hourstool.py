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
        self.batchConvert(srcRoot, bystationDir)

        # 08-08, qixiang
        subdir = "qx0808"
        dailyDir = os.path.join(targetRoot, subdir, "daily0808")
        monthlyDir = os.path.join(targetRoot, subdir, "monthly0808")
        yearDir = os.path.join(targetRoot, subdir, "year0808")

        self.statisticsDaily(bystationDir, dailyDir, "0808")
        self.statisticsMonthly(dailyDir, monthlyDir)
        self.statisticsYears(monthlyDir, yearDir)

        # 20-20, qixiang
        subdir = "qx2020"
        dailyDir = os.path.join(targetRoot, subdir, "daily2020")
        monthlyDir = os.path.join(targetRoot, subdir, "monthly2020")
        yearDir = os.path.join(targetRoot, subdir, "year2020")

        self.statisticsDaily(bystationDir, dailyDir, "2020")
        self.statisticsMonthly(dailyDir, monthlyDir)
        self.statisticsYears(monthlyDir, yearDir)

        # 08-08, shuili
        subdir = "sl0808"
        dailyDir = os.path.join(targetRoot, subdir,  "daily0808")
        monthlyDir = os.path.join(targetRoot, subdir, "monthly0808")
        yearDir = os.path.join(targetRoot, subdir, "year080800")

        self.statisticsDaily(bystationDir, dailyDir, "0832")
        self.statisticsMonthly(dailyDir, monthlyDir)
        self.statisticsYears(monthlyDir, yearDir)

    def batchConvert(self, srcPathRoot, targetPathRoot):
        self.clearDirectory(targetPathRoot)
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

            if items[7] == "999990":
                items[7] == "0"
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

    def statisticsDaily(self, srcPathRoot, targetPathRoot, stat_win):
        self.clearDirectory(targetPathRoot)
        filelist = os.listdir(srcPathRoot)
        for item in filelist:
            srcPath = os.path.join(srcPathRoot, item)
            targetPath = os.path.join(targetPathRoot, item)
            self.stasticsDailySingleStatation(item, srcPath,
                                              targetPath, stat_win)

    def stasticsDailySingleStatation(self, sid, srcPath, targetPath, stat_win):
        print("processing {0}".format(srcPath))
        db = pd.read_table(srcPath, skip_blank_lines=True,
                           delim_whitespace=True, index_col="DATETIME")
        result = []
        # todo: do config the range of loop

        year = 2010
        endDay = date(2020, 1, 1)
        curDay = date(year, 1, 1)
        while(curDay < endDay):
            if stat_win == "0808":
                recs = self.queryData(db, curDay, 16)
            elif stat_win == "2020":
                recs = self.queryData(db, curDay, 4)
            else:
                recs = self.queryData(db, curDay, -8)

            if not recs.empty:
                day_rec = self.calcDaily(sid, curDay, recs, stat_win)
                if day_rec is not None:
                    result.append(day_rec)
            curDay = curDay + timedelta(days=1)

        if stat_win == "0808" or stat_win == "0832":
            header = ("{:>8}{:>10}{:>6}{:>4}{:>4}{:>10}{:>10}{:>10}{:>10}"
                      "{:>10}{:>10}{:>10}{:>4}{:>10}{:>4}{:>10}{:>4}\n") \
                .format("SID", "DATE", "YEAR", "MON", "DAY",
                        "AVG_PRES", "MAX_PRES", "MIN_PRES",
                        "AVG_TEMP", "MAX_TEMP", "MIN_TEMP",
                        "PREC24", "CNT", "PREC08_20", "C1", "PREC20_08", "C2")
        else:
            header = ("{:>8}{:>10}{:>6}{:>4}{:>4}{:>10}{:>10}{:>10}{:>10}"
                      "{:>10}{:>10}{:>10}{:>4}{:>10}{:>4}{:>10}{:>4}\n") \
                .format("SID", "DATE", "YEAR", "MON", "DAY",
                        "AVG_PRES", "MAX_PRES", "MIN_PRES",
                        "AVG_TEMP", "MAX_TEMP", "MIN_TEMP",
                        "PREC24", "CNT", "PREC20_08", "C1", "PREC08_20", "C2")

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

    def calcDaily(self, sid, dt, hours24, stat_win):
        """
        http://www.szmb.gov.cn/quf/2009/08/2017101815192310488.pdf
        """
        if (len(hours24) > 24):

                self._logger.error(("{1}-{2:0>2d}-{3:0>2d},  "
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
                    self._logger.error(("{1}-{2:0>2d}-{3:0>2d},  "
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
                    self._logger.error(("{1}-{2:0>2d}-{3:0>2d},  "
                                        "Station {0} miss temperature at"
                                        "[02, 08, 14, 20]")
                                       .format(sid, dt.year, dt.month, dt.day))

            # statistics precipation
            valid_prec = hours24.query("200 > PREC >= 0")
            prec24 = valid_prec["PREC"].sum()
            prec24_cnt = len(valid_prec)

            am_prec = valid_prec.query("HR <=8 | HR>20")
            pm_prec = valid_prec.query("8 <  HR <= 20")

            prec12_am = am_prec["PREC"].sum()
            prec12_am_cnt = len(am_prec)
            prec12_pm = pm_prec["PREC"].sum()
            prec12_pm_cnt = len(pm_prec)

            if stat_win == "0808" or stat_win == "0832":
                rec = ("{:>8}{:>10}{:>6}{:>4}{:>4}{:>10.1f}{:>10.1f}{:>10.1f}"
                       "{:>10.1f}{:>10.1f}{:>10.1f}"
                       "{:>10.1f}{:>4d}{:>10.1f}{:>4d}{:>10.1f}{:>4d}\n") \
                    .format(sid, dt.strftime("%Y%m%d"),
                            dt.year, dt.month, dt.day,
                            avg_pres, max_pres, min_pres,
                            avg_temp, max_temp, min_temp,
                            prec24, prec24_cnt, prec12_pm,
                            prec12_pm_cnt, prec12_am, prec12_am_cnt)
            else:
                rec = ("{:>8}{:>10}{:>6}{:>4}{:>4}{:>10.1f}{:>10.1f}{:>10.1f}"
                       "{:>10.1f}{:>10.1f}{:>10.1f}"
                       "{:>10.1f}{:>4d}{:>10.1f}{:>4d}{:>10.1f}{:>4d}\n") \
                    .format(sid, dt.strftime("%Y%m%d"),
                            dt.year, dt.month, dt.day,
                            avg_pres, max_pres, min_pres,
                            avg_temp, max_temp, min_temp,
                            prec24, prec24_cnt, prec12_am, prec12_am_cnt,
                            prec12_pm, prec12_pm_cnt)
            return rec

    def statisticsMonthly(self, srcPathRoot, targetPathRoot):
        self.clearDirectory(targetPathRoot)
        filelist = os.listdir(srcPathRoot)
        for item in filelist:
            srcPath = os.path.join(srcPathRoot, item)
            targetPath = os.path.join(targetPathRoot, item)
            self.stasticsMonthSingleStatation(item, srcPath, targetPath)

    def stasticsMonthSingleStatation(self, sid, srcPath, targetPath):
        db = pd.read_table(srcPath, skip_blank_lines=True,
                           delim_whitespace=True, index_col="DATE")
        result = []
        # todo: do config the range of loop

        for year in range(2010, 2020):
            for mon in range(1, 13):
                cond = "YEAR == {0} & MON == {1}".format(year, mon)
                recs = db.query(cond)
                if not recs.empty:
                    mon_rec = self.calcMonthly(sid, year, mon, recs)
                    result.append(mon_rec)

        header = ("{:>8}{:>6}{:>4}{:>10}{:>10}{:>10}{:>10}"
                  "{:>10}{:>10}{:>10}{:>4}\n").format(
                      "SID", "YEAR", "MON",
                      "AVG_PRES", "MAX_PRES", "MIN_PRES",
                      "AVG_TEMP", "MAX_TEMP", "MIN_TEMP",
                      "PREC_MON", "CNT")
        with open(targetPath, 'w') as fo:
            fo.write(header)
            fo.writelines(result)
        fo.close()

    def calcMonthly(self, sid, year, mon, recs):
        if len(recs) > 0:
            # statistics pressure
            valid_pressure = recs.query("1200 > AVG_PRES > 800")
            # print(valid_pressure)
            if len(valid_pressure) >= 24:
                avg_pres = valid_pressure["AVG_PRES"].mean()
                max_pres = valid_pressure["MAX_PRES"].max()
                min_pres = valid_pressure["MIN_PRES"].min()
            else:
                avg_pres = 999999
                max_pres = 999999
                min_pres = 999999
                self._logger.error(("{1}-{2:0>2d},  "
                                    "Station {0} miss pressure.")
                                   .format(sid, year, mon))

            # statistics temperature
            valid_temperature = recs.query("60 > AVG_TEMP > -60")
            # print(valid_temperature)
            if len(valid_temperature) >= 24:
                avg_temp = valid_temperature["AVG_TEMP"].mean()
                max_temp = valid_temperature["MAX_TEMP"].max()
                min_temp = valid_temperature["MIN_TEMP"].min()
            else:
                avg_temp = 999999
                max_temp = 999999
                min_temp = 999999
                self._logger.error(("{1}-{2:0>2d},  "
                                    "Station {0} miss temperature")
                                   .format(sid, year, mon,))

            # statistics precipation
            valid_prec = recs.query("500 > PREC24 >= 0")
            prec_mon = valid_prec["PREC24"].sum()
            prec_cnt = len(valid_prec)

            rec = ("{:>8}{:>6}{:>4}{:>10.1f}{:>10.1f}{:>10.1f}"
                   "{:>10.1f}{:>10.1f}{:>10.1f}{:>10.1f}{:>4d}\n") \
                .format(sid, year, mon, avg_pres, max_pres, min_pres,
                        avg_temp, max_temp, min_temp, prec_mon, prec_cnt)
            return rec

    def statisticsYears(self, srcPathRoot, targetPathRoot):
        self.clearDirectory(targetPathRoot)
        filelist = os.listdir(srcPathRoot)
        for item in filelist:
            srcPath = os.path.join(srcPathRoot, item)
            targetPath = os.path.join(targetPathRoot, item)
            self.stasticsYearSingleStatation(item, srcPath, targetPath)

    def stasticsYearSingleStatation(self, sid, srcPath, targetPath):
        db = pd.read_table(srcPath, skip_blank_lines=True,
                           delim_whitespace=True, index_col=["YEAR", "MON"])
        result = []
        # todo: do config the range of loop

        for year in range(2010, 2020):
            cond = "YEAR == {0}".format(year)
            recs = db.query(cond)
            if not recs.empty:
                mon_rec = self.calcYear(sid, year, recs)
                result.append(mon_rec)

        header = ("{:>8}{:>6}{:>10}{:>10}{:>10}{:>10}"
                  "{:>10}{:>10}{:>10}{:>4}\n").format(
                      "SID", "YEAR",
                      "AVG_PRES", "MAX_PRES", "MIN_PRES",
                      "AVG_TEMP", "MAX_TEMP", "MIN_TEMP",
                      "PREC_Y", "CNT")
        with open(targetPath, 'w') as fo:
            fo.write(header)
            fo.writelines(result)
        fo.close()

    def calcYear(self, sid, year, recs):
        if len(recs) > 0:
            # statistics pressure
            valid_pressure = recs.query("1200 > AVG_PRES > 800")
            if len(valid_pressure) >= 10:
                avg_pres = valid_pressure["AVG_PRES"].mean()
                max_pres = valid_pressure["MAX_PRES"].max()
                min_pres = valid_pressure["MIN_PRES"].min()
            else:
                avg_pres = 999999
                max_pres = 999999
                min_pres = 999999
                self._logger.error(("{1}, Station {0} miss pressure.")
                                   .format(sid, year))

            # statistics temperature
            valid_temperature = recs.query("60 > AVG_TEMP > -60")
            if len(valid_temperature) >= 10:
                avg_temp = valid_temperature["AVG_TEMP"].mean()
                max_temp = valid_temperature["MAX_TEMP"].max()
                min_temp = valid_temperature["MIN_TEMP"].min()
            else:
                avg_temp = 999999
                max_temp = 999999
                min_temp = 999999
                self._logger.error(("{1}, Station {0} miss temperature")
                                   .format(sid, year))

            # statistics precipation
            valid_prec = recs.query("5000 > PREC_MON >= 0")
            prec_year = valid_prec["PREC_MON"].sum()
            prec_cnt = len(valid_prec)

            rec = ("{:>8}{:>6}{:>10.1f}{:>10.1f}{:>10.1f}"
                   "{:>10.1f}{:>10.1f}{:>10.1f}{:>10.1f}{:>4d}\n") \
                .format(sid, year, avg_pres, max_pres, min_pres,
                        avg_temp, max_temp, min_temp, prec_year, prec_cnt)
            return rec

    def clearDirectory(self, targetRoot):
        if os.path.exists(targetRoot) and len(os.listdir(targetRoot)) > 0:
            print("\nThe dir of {0} is not empty and will been overrided."
                  .format(targetRoot))
            shutil.rmtree(targetRoot, True)
            time.sleep(1)
        if not os.path.exists(targetRoot):
            os.makedirs(targetRoot)


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
