#!c:/Python26/ArcGIS10.0/python.exe
# -*- coding: utf-8 -*-
#COPYRIGHT 2016 igsnrr
#
#MORE INFO ...
#email:
"""The Series class is designed to represent a Series and its attributes."""
# ######!/usr/bin/python

import numpy as np

class SeriesWithLocation:
    def __init__(self, index, i, j, x, y,data):
        self._version = "SeriesWithLocation.py 0.0.1"
        self.index = index
        self.i = i
        self.j = j
        self.x = x
        self.y = y
        self.data = data

    @property
    def toString(self):
        # todo: format later


        sSeries = np.array2string(self.data)
        # it works above numpy v1.10
        # sSeries = np.array2string(self.data, formatter={'float_kind': lambda x: "%10.4f" % x})

        sline = "%8d %8d %8d %16.4f %16.4f %s\n" % (self.index, self.i, self.j, self.x, self.y, sSeries.strip("[]").replace("\n", ""))

        return sline

if __name__ == "__main__":
    # testing code

    s = SeriesWithLocation(10, 2, 3, 1000.1, 2000.2, np.array([0.0, 1.1, 2.2, 3.3]) )
    print(s.toString)

else:
    print("loading SeriesWithLocation module")