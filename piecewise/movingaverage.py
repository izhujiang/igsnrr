# -*- coding: utf-8 -*-
import os
# import math
# from datetime import timedelta, datetime
# from datetime import datetime

# import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt


def doMovingAverages(df, rolling_win_size=31, min_periods=31):
    df['NDVI_AVG'] = df['NDVI'].rolling(window=rolling_win_size, min_periods=min_periods, center=True).mean()
    df['EVI_AVG'] = df['EVI'].rolling(window=rolling_win_size, min_periods=min_periods, center=True).mean()

    # ndvi_avg = df['NDVI_AVG'].to_numpy()

# def doDisplay(df):
#     # Plot outputs
#     (cn_row, cn_col) = df.shape
#     # x = df['DOY']

#     ndvi_avg =df['NDVI_AVG']
#     evi_avg =df['EVI_AVG']

#     plt.figure(figsize=FIG_SIZE)
#     plt.xlim(left=0, right=cn_row)
#     plt.ylim(bottom=0, top=0.4)

#     ndvi_avg_line, = plt.plot(x, ndvi_avg, label="NDVI_AVG", linewidth=1)
#     evi_avg_line, = plt.plot(x, evi_avg, label="EVI_AVG", linewidth=1)

#     handles=[ndvi_avg_line,
#              evi_avg_line]

#     plt.legend(handles = handles, loc='upper right')


# paramters that affact the result
#
# the sie of figure, unit: inch
FIG_SIZE = (16, 12)
DISPLAY_ENABLE = False
DEBUG_ENABLE = False

# ----------------------------
# explore ndvi data and find potential segment points
rolling_win_size = 31
min_periods = 28
# input_file = "/Users/jiangzhu/workspace/igsnrr/data/mcd43a4/subfolder/1.csv"
# output_file = "/Users/jiangzhu/workspace/igsnrr/data/mcd43a4/average-folder/1.csv"
input_dir = "/Users/jiangzhu/workspace/igsnrr/data/mcd43a4/subfolder"
output_dir = "/Users/jiangzhu/workspace/igsnrr/data/mcd43a4/average-folder"

src_files = os.listdir(input_dir)
for fname in src_files:
    input_file = os.path.join(input_dir, fname)
    output_file = os.path.join(output_dir, fname)
    if os.path.isfile(input_file):
        print("doing moving-window-average: " + input_file)
        df = pd.read_csv(input_file, sep=',')
                 # , names=["system:index", \
                # "EVI", \
                # "NDVI", \
                # "Nadir_Reflectance_Band1", \
                # "Nadir_Reflectance_Band2", \
                # "Nadir_Reflectance_Band3", \
                # "Nadir_Reflectance_Band4", \
                # "Nadir_Reflectance_Band5", \
                # "Nadir_Reflectance_Band6", \
                # "Nadir_Reflectance_Band7", \
                # "date", \
                # "oid", \
                # "geo" ])

        # print(df.head())
        doMovingAverages(df, rolling_win_size, min_periods)
        # if DISPLAY_ENABLE:
            # doDisplay(df)
        df.to_csv( path_or_buf=output_file, sep=',')