#!D:/Python27/python.exe
#coding=utf-8

import os
import sys
import numpy as np
import numpy.random as ran
from idlpy import IDL
thisfile__abspath = os.path.realpath(os.path.abspath(__file__))


class EllipsoidWrapper(object):
    def __init__(self):
        super(self.__class__, self).__init__()
        curPath = os.path.split(thisfile__abspath)[0]
        savFilePath = os.path.join(curPath, "ellipsoid.sav")
        IDL.run('restore, FILENAME = \'{0}\''.format(savFilePath), stdout=True)

    def top2wgs(self, top_latitude, top_elevation):
        IDL.top_latitude = top_latitude
        IDL.top_elevation = top_elevation

        wgs_latitude = None
        IDL.wgs_latitude = wgs_latitude
        wgs_elevation = None
        IDL.wgs_elevation = wgs_elevation

        # IDL.run('print, top_latitude, top_elevation', stdout=True)
        # IDL.run('print, wgs_latitude, wgs_elevation', stdout=True)

        IDL.run('top2wgs, top_latitude, top_elevation, wgs_latitude, wgs_elevation', stdout=True)
        wgs_latitude = IDL.wgs_latitude  # pass by value
        wgs_elevation = IDL.wgs_elevation  # pass by value

        return wgs_latitude, wgs_elevation

if __name__ == "__main__":

    ew = EllipsoidWrapper()
    top_latitude = ran.rand(5)
    top_elevation = ran.rand(5)

    wgs_latitude2, wgs_elevation2 = ew.top2wgs(top_latitude, top_elevation)
    print(wgs_latitude2)
    print(wgs_elevation2)

else:
    print("loading ellipsowrapper module")
