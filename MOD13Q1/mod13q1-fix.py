# -*- coding: utf-8 -*-
import os

# import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def fixByMovingAverages(df, rolling_win_size=3, min_periods=1, max_adj_num=5):
    df['NDVI_ADJ'] =df['NDVI']
    df['EVI_ADJ'] =df['EVI']
    (row_num, col_num) = df.shape
    # for i in range(max_adj_num):
    #     df['NDVI_AVG'] = df['NDVI_ADJ'].rolling(window=rolling_win_size, min_periods=min_periods, center=True).mean()
    #     df['NDVI_DIF'] = df['NDVI_ADJ'] - df['NDVI_AVG']

    #     idxmin = df['NDVI_DIF'].idxmin()
    #     if df.loc[idxmin, 'NDVI_DIF'] >= 0:
    #         print("NDVI smothing by moving average stop loop at ", i)
    #         break
    #     # df['NDVI_ADJ'][idxmin] = df['NDVI_AVG'][idxmin]
    #     df.loc[idxmin, 'NDVI_ADJ'] = df.loc[idxmin, 'NDVI_AVG']

    for i in range(max_adj_num):
        df['NDVI_TEMP']=df['NDVI_ADJ']
        df['NDVI_AVG'] = df['NDVI_ADJ'].rolling(window=rolling_win_size, min_periods=min_periods, center=True).mean()

        stopLoop = True
        for r_index in range(1, row_num -1):
            if df.loc[r_index, 'NDVI_ADJ'] < df.loc[r_index - 1, 'NDVI_ADJ'] and df.loc[r_index, 'NDVI_ADJ'] < df.loc[r_index + 1, 'NDVI_ADJ']:
                df.loc[r_index, 'NDVI_TEMP']  =  df.loc[r_index, 'NDVI_AVG']
                stopLoop = False
        if stopLoop == True:
            print("NDVI smothing by moving average stop loop at ", i)
            break
        df['NDVI_ADJ'] = df['NDVI_TEMP']

    # for i in range(adjust_num):
    #     df['EVI_AVG'] = df['EVI_ADJ'].rolling(window=rolling_win_size, min_periods=min_periods, center=True).mean()
    #     df['EVI_DIF'] = df['EVI_ADJ'] - df['EVI_AVG']
    #     idxmin = df['EVI_DIF'].idxmin()
    #     if df.loc[idxmin, 'EVI_DIF'] >= 0:
    #         print("EVI smothing by moving average stop loop at ", i)
    #         break
    #     # df['EVI_ADJ'][idxmin] = df['EVI_AVG'][idxmin]
    #     df.loc[idxmin, 'EVI_ADJ'] = df.loc[idxmin, 'EVI_AVG']
    for i in range(max_adj_num):
        df['EVI_TEMP']=df['EVI_ADJ']
        df['EVI_AVG'] = df['EVI_ADJ'].rolling(window=rolling_win_size, min_periods=min_periods, center=True).mean()

        stopLoop = True
        for r_index in range(1, row_num -1):
            if df.loc[r_index, 'EVI_ADJ'] < df.loc[r_index - 1, 'EVI_ADJ'] and df.loc[r_index, 'EVI_ADJ'] < df.loc[r_index + 1, 'EVI_ADJ']:
                df.loc[r_index, 'EVI_TEMP']  =  df.loc[r_index, 'EVI_AVG']
                stopLoop = False
        if stopLoop == True:
            print("EVI smothing by moving average stop loop at ", i)
            break
        df['EVI_ADJ'] = df['EVI_TEMP']
    # print(df)

def fixByFillgaps(df, max_fill_num=10):
    df['NDVI_FILL'] =df['NDVI']
    df['EVI_FILL'] =df['EVI']
    (row_num, col_num) = df.shape
    # print(row_num)

    # process NDVI
    for i in range(max_fill_num):
        df['NDVI_TEMP']=df['NDVI_FILL']
        stopLoop = True
        for r_index in range(1, row_num -1):
            if df.loc[r_index, 'NDVI_FILL'] < df.loc[r_index - 1, 'NDVI_FILL'] and df.loc[r_index, 'NDVI_FILL'] < df.loc[r_index + 1, 'NDVI_FILL']:
                df.loc[r_index, 'NDVI_TEMP']  = (df.loc[r_index - 1, 'NDVI_FILL']+ df.loc[r_index + 1, 'NDVI_FILL']) / 2
                stopLoop = False
        if stopLoop == True:
            print("NDVI filling stop loop at ", i)
            break
        df['NDVI_FILL'] = df['NDVI_TEMP']

    # process EVI
    for i in range(max_fill_num):
        df['EVI_TEMP']=df['EVI_FILL']
        stopLoop = True
        for r_index in range(1, row_num -1):
            if df.loc[r_index, 'EVI_FILL'] < df.loc[r_index - 1, 'EVI_FILL'] and df.loc[r_index, 'EVI_FILL'] < df.loc[r_index + 1, 'EVI_FILL']:
                df.loc[r_index, 'EVI_TEMP']  = (df.loc[r_index - 1, 'EVI_FILL']+ df.loc[r_index + 1, 'EVI_FILL']) / 2
                stopLoop = False
        if stopLoop == True:
            print("EVI filling stop loop at ", i)
            break
        df['EVI_FILL'] = df['EVI_TEMP']

def doDisplay(df):
    # Plot outputs
    (cn_row, cn_col) = df.shape
    x = df['Date']

    ndvi =df['NDVI']
    ndvi_adj =df['NDVI_ADJ']
    ndvi_fill =df['NDVI_FILL']

    evi =df['EVI']
    evi_adj =df['EVI_ADJ']
    evi_fill =df['EVI_FILL']
    # evi_fill =df['EVI_FILL']
    # print(ndvi, ndvi_adj)

    plt.figure(figsize=FIG_SIZE)
    plt.xlim(left=0, right=cn_row)
    plt.ylim(bottom=0.025, top=0.1)

    ndvi_line, = plt.plot(x, ndvi, label="NDVI", linewidth=1)
    ndvi_adj_line, = plt.plot(x, ndvi_adj, label="NDVI_ADJ", linewidth=1)
    ndvi_fill_line, = plt.plot(x, ndvi_fill, label="NDVI_FILL", linewidth=1)

    evi_line, = plt.plot(x, evi, label="EVI", linewidth=1)
    evi_adj_line, = plt.plot(x, evi_adj, label="EVI_ADJ", linewidth=1)
    evi_fill_line, = plt.plot(x, evi_fill, label="EVI_FILL", linewidth=1)

    # handles=[ndvi_line, ndvi_adj_line]
    handles=[ndvi_line, ndvi_adj_line, ndvi_fill_line, evi_line, evi_adj_line, evi_fill_line]

    plt.legend(handles = handles, loc='upper right')


# paramters that affact the result
#
# the sie of figure, unit: inch
FIG_SIZE = (16, 12)
DISPLAY_ENABLE = True
DEBUG_ENABLE = False

# ----------------------------
# explore ndvi data and find potential segment points
rolling_win_size = 3
min_periods = 3
adjust_num = 5
fill_num = 20

input_dir = "/Users/jiangzhu/workspace/igsnrr/data/MOD13Q1/input"
output_dir = "/Users/jiangzhu/workspace/igsnrr/data/MOD13Q1/output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

src_files = os.listdir(input_dir)
for fname in src_files:
    input_file = os.path.join(input_dir, fname)
    output_file = os.path.join(output_dir, fname)
    if os.path.isfile(input_file):
        df = pd.read_csv(input_file, sep="\t", header=None, names=["Well","Date", "EVI", "NDVI", "VI_Quality"])
        # print(df.head())

        fixByMovingAverages(df, rolling_win_size, min_periods, adjust_num)

        fixByFillgaps(df, fill_num)

        if DISPLAY_ENABLE:
            doDisplay(df)

        columns = ["Well","Date", "EVI","EVI_ADJ","EVI_FILL", "NDVI", "NDVI_ADJ","NDVI_FILL", "VI_Quality"]
        df.to_csv( path_or_buf=output_file, sep=',', columns=columns)