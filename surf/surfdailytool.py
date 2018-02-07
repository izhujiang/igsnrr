# !/usr/bin/python
# -*- coding: utf-8 -*-
# COPYRIGHT 2016 igsnrr
#
# MORE INFO ...
# email:

import os
import shutil
import time
from datetime import date, timedelta

from igsnrr.base.toolbase import ToolBase


class SurfDailyTool(ToolBase):
    """The tool is designed to convert surf daily statisics files orgarnized \
    by month into files by station IDs ."""
    def __init__(self):
        ToolBase.__init__(self, "SurfDailyTool",
                          "The SurfDaily Tool convert surf daily statisics files organized \
                          by month into files organized by station.")
        self._version = "surf4hourstool.py 0.0.1"

    def defineArgumentParser(self, parser):
        parser.add_argument(
                "subcmd", action="store",
                help="Supporting Subcommands (convert, filter, prec_events).")
        parser.add_argument("source", action="store",
                            help="root dir for source files")
        parser.add_argument("target", action="store",
                            help="root dir for target files")
        parser.add_argument("--begin", action="store",
                            help="beginning date that filter")
        parser.add_argument("--end", action="store",
                            help="the last day of the filter")

    def run(self, args):
        subcmd = args.subcmd
        if subcmd == "convert":
            srcRoot = args.source
            targetRoot = args.target
            print(srcRoot, "-->", targetRoot)

            # bystationDir = os.path.join(targetRoot, "bystation")
            bystationDir = targetRoot
            self.batchConvert(srcRoot, bystationDir)
        elif subcmd == "filter":
            srcRoot = args.source
            targetRoot = args.target
            dayFrom = args.begin
            dayTo = args.end
            self.filterSurfDaily(srcRoot, targetRoot, dayFrom, dayTo)
        elif subcmd == "prec_events":
            srcRoot = args.source
            targetRoot = args.target
            self.statisicsPrecEvent(srcRoot, targetRoot)

    def batchConvert(self, srcPathRoot, targetPathRoot):
        self.clearDirectory(targetPathRoot)
        filelist = sorted(os.listdir(srcPathRoot))

        for item in filelist:
            if item.endswith(".TXT") or item.endswith(".txt"):
                srcPath = os.path.join(srcPathRoot, item)
                print(srcPath)
                self.convert(srcPath, targetPathRoot)

        filelist = sorted(os.listdir(targetPathRoot))
        for item in filelist:
            targetFile = os.path.join(targetPathRoot, item)
            self.insertMissingData(targetFile, targetFile)

    def convert(self, srcPath, targetRoot):
        if not os.path.exists(srcPath):
            self._loggej.info("Failed: {0} does't existe".format(srcPath))

        recs = []
        with open(srcPath) as f:
            recs = f.readlines()
            # recs = recs[2:]
        f.close()

        items_cnt = len(recs[0].split())
        element_cnt = int((items_cnt - 7) / 2)
        group = {}
        strfmt = (
                "{0:>8}{1:>8d}{2:>8d}{3:>8d}"
                "{4:>8d}{5:0>2d}{6:0>2d}{4:>8d}{5:>4d}{6:>4d}{7}\n")

        for rec in recs:
            items = rec.split()
            if items[0] not in group:
                group[items[0]] = []

            if(len(items) < items_cnt):
                print("check the error record: ")
                self._logger.error(items)
                continue

            val = ""
            for i in range(element_cnt):
                val = val + "{:>8d}".format(int(items[7 + i]))
            for i in range(element_cnt):
                val = val + "{:>3d}".format(int(items[7 + element_cnt + i]))

            rec = strfmt.format(items[0], int(items[1]), int(items[2]),
                                int(items[3]), int(items[4]), int(items[5]),
                                int(items[6]), val)

            group[items[0]].append(rec)

        for k, v in group.items():
            target = os.path.join(targetRoot, k)

            recs_w = group[k]
            # recs_w = [ strfmt.format(k, year, mon, day, i, 999999,
            # 999999, 999999) for i in range(24)]

            # for line in v:
            #     items = line.split()
            #     recs_w[int(items[5])] = line

            with open(target, 'a') as fo:
                fo.writelines(recs_w)
            fo.close()

    def insertMissingData(self, srcFilePath, destFilePath):
        with open(srcFilePath) as f:
            recs = f.readlines()
        f.close()

        if len(recs) == 0:
            return

        first_rec = recs[0]
        last_rec = recs[len(recs)-1]
        recs_filled = []
        items = first_rec.split()
        firstday = date(int(items[5]), int(items[6]), int(items[7]))
        sid = items[0]
        items = last_rec.split()
        lastday = date(int(items[5]), int(items[6]), int(items[7]))

        element_cnt = int((len(first_rec.split()) - 7) / 2)
        strfmt = (
                "{0:>8}{1:>8d}{2:>8d}{3:>8d}"
                "{4:>8d}{5:0>2d}{6:0>2d}{4:>8d}{5:>4d}{6:>4d}{7}\n")
        # strfmt = (
        #         "{0:>8}{1:>8d}{2:>8d}{3:>8d}"
        #         "{4:>8d}{5:0>2d}{6:0>2d}{4:>8d}{5:>4d}{6:>4d}"
        #         "{7:>8d}{7:>8d}{7:>8d}{8:>3d}{8:>3d}{8:>3d}\n")
        dv = 32700
        df = 8
        lat = dv
        lon = dv
        alt = dv

        ds = firstday
        day_cnt = (lastday - firstday).days + 1
        missingV = (
                "{:>8d}".format(dv) * element_cnt +
                "{:>3d}".format(df) * element_cnt)
        for i in range(day_cnt):
            rec = strfmt.format(
                    sid, lat, lon, alt, ds.year, ds.month, ds.day, missingV)
            recs_filled.append(rec)
            ds = ds + timedelta(days=1)

        for rec in recs:
            items = rec.split()
            ds = date(int(items[5]), int(items[6]), int(items[7]))
            recs_filled[(ds - firstday).days] = rec

        with open(destFilePath, 'w') as fo:
            fo.writelines(recs_filled)
        fo.close()

    def filterSurfDaily(self, srcRoot, targetRoot, dayFrom, dayTo):
        self.clearDirectory(targetRoot)
        filelist = sorted(os.listdir(srcRoot))

        for item in filelist:
            srcPath = os.path.join(srcRoot, item)
            targetPath = os.path.join(targetRoot, item)
            self.filterDailySingleStatation(
                    item, srcPath, targetPath, dayFrom, dayTo)

    def filterDailySingleStatation(
            self, sid, srcPath, targetPath, dayFrom, dayTo):
        df = int(dayFrom)
        dt = int(dayTo)
        recs = []
        with open(os.path.join(srcRoot, sid)) as f:
            recs = f.readlines()
        f.close()

        recs_filter = [
                rec for rec in recs
                if self.betweenDays(rec, df, dt)]

        with open(os.path.join(targetRoot, sid), 'w') as fo:
            fo.writelines(recs_filter)
        fo.close()

    def statisicsPrecEvent(self, srcRoot, targetRoot):
        self.clearDirectory(targetRoot)
        filelist = sorted(os.listdir(srcRoot))

        for item in filelist:
            if not item.startswith("."):
                srcPath = os.path.join(srcRoot, item)
                targetPath = os.path.join(targetRoot, item)

                print("PrecEvent: " + srcPath + " --> " + targetPath)
                self.statisicsPrecEventSingleStation(srcPath, targetPath)

    def statisicsPrecEventSingleStation(self, srcPath, targetPath):
        with open(srcPath) as f:
            recs = f.readlines()
        f.close()

        flags = list(map(isRainday, recs))
        flags.insert(0, 0)
        flags.append(0)

        vFlags = [flags[i] - flags[i-1] for i in range(1, len(flags))]
        # print(vFlags)

        startIndexs = []
        endIndexs = []
        for i in range(len(vFlags)):
            if vFlags[i] == 1:
                startIndexs.append(i)
            elif vFlags[i] == -1:
                endIndexs.append(i)
            else:
                pass

        if len(startIndexs) != len(endIndexs):
            self._logger.Warning(
                    "Checking codes ... unequal length "
                    "of startIndexs and endIndexs")

        recs_events = []

        strfmt = (
                "{0:>8}{1:>8d}{2:>8d}{3:>8d}"
                "{4:>8d}{5:0>2d}{6:0>2d}")
        #        "{4:>8d}{5:>4d}{6:>4d}")
        strfmt2 = "{0}{1:>8d}{2:0>2d}{3:0>2d}{4:8d}{5:10d}\n"

        for i in range(len(startIndexs)):
            rain_start = recs[startIndexs[i]].split()
            rain_end = recs[endIndexs[i] - 1].split()
            sid = rain_start[0]
            lat = int(rain_start[1])
            lon = int(rain_start[2])
            alt = int(rain_start[3])
            # ymd = rain_start[4]
            year = int(rain_start[5])
            mon = int(rain_start[6])
            day = int(rain_start[7])
            rec = strfmt.format(
                    sid, lat, lon, alt,
                    year, mon,  day)

            prec24 = 0
            rain_last = endIndexs[i] - startIndexs[i]
            for j in range(startIndexs[i],  endIndexs[i]):
                prec24 = prec24 + int(recs[j].split()[10])

            year = int(rain_end[5])
            mon = int(rain_end[6])
            day = int(rain_end[7])
            rec2 = strfmt2.format(rec, year, mon, day, rain_last, prec24)

            recs_events.append(rec2)

        with open(targetPath, 'w') as fo:
            fo.writelines(recs_events)
        fo.close()

    def clearDirectory(self, targetRoot):
        if os.path.exists(targetRoot) and len(os.listdir(targetRoot)) > 0:
            print("\nThe dir of {0} is not empty and will been overrided."
                  .format(targetRoot))
            shutil.rmtree(targetRoot, True)
            time.sleep(1)
        if not os.path.exists(targetRoot):
            os.makedirs(targetRoot)

    def betweenDays(self, cur_rec, dayFrom, dayTo):
        items = cur_rec.split()
        if dayFrom <= int(items[4]) and int(items[4]) <= dayTo:
            return True
        else:
            return False


def isRainday(rec):
    items = rec.split()
    return 1 if 0 < int(items[10]) < 1000 else 0


if __name__ == "__main__":
    # testing code
    # import sys
    # print(sys.argv)
    tool = SurfDailyTool()
    import argparse
    from ..base.logger import Logger
    parser = argparse.ArgumentParser(prog="python.exe3 -m surfdailystool",
                                     description="SurfDailyTool Usage Guide",
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
