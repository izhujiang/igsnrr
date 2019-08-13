#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 10:56:04 2019

@author: jiangzhu
"""

import pandas as pd
import matplotlib.pyplot as plt

def plotSingleCoefByRollingWin(df, rolling_win):
    wdf = df[df["RollingWin"] == rolling_win]
    x = wdf['PotentialInflection']
    coef =wdf['MaxCoef']
    coef_line, = plt.plot(x, coef, label="MaxCoef{0}".format(rolling_win), linewidth=1)
    return coef_line

FIG_SIZE=(12,8)
DRAW_MODE = 'SINGLE'  # or 'MULTIPLE'
ROLLING_WIN = 15
# DRAW_MODE = 'MULTIPLE'
# read from file
df = pd.read_csv("./coef_20190812185120.log", sep='\t', header=None)
cols_header = ["RollingWin", "PotentialInflection", "SegmentCount", "MaxCoef", "Inflection"]
df.columns = cols_header


# display by RollingWin
plt.figure(figsize=FIG_SIZE)
plt.xlim(left=0, right=55) 
plt.ylim(bottom=0.8, top=1)

if DRAW_MODE == 'SINGLE':
    coef_line = plotSingleCoefByRollingWin(df, ROLLING_WIN)
    handles=[coef_line]
    plt.legend(handles = handles, loc='upper right')
else:
    handles=[None]* 14
    for rw in range(5,32,2):
        ceof_line = plotSingleCoefByRollingWin(df, rw)
        handles[int((rw - 5)/2)] = ceof_line
     
    plt.legend(handles = handles, loc='upper right')

