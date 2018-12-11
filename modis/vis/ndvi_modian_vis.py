#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


#---------------------------------
# input and output parameters, modify here if you need
filename = "ndvi-modian2018"
data_url = "../../data/ndvi/" + filename + ".csv"
output_path = "../../data/ndvi/" + filename + ".png"

show_enable = True

# visualizaion parameters
xlim_min, xlim_max = 850, 1000  # visiable extent of axix_x[0-1000) according to the input file
tick_step = 20        # interval between ticks on axix_x
fig_size = [6.4, 4.8] # size(in inches) of figure.

dpi = 300

#---------------------------------
# plt.ion()   # run in interactive mode
# plt.ioff()   # or in batch mode


df =  pd.read_csv(data_url)
[x, x_labels,ndvi,evi] = np.split( df[["system:index", "NDVI", "NDVI_Area", "EVI_Area"]].values, 4, 1);
x = x.ravel()
x_labels = x_labels.ravel()
ndvi = ndvi.ravel()
evi = evi.ravel()

fig = plt.figure(1, clear=True, figsize=fig_size )  
plt.title("Seanonal mesian NDVI and EVI' CDF")

# Pad margins so that markers don't get clipped by the axes
# plt.margins(1)
plt.subplots_adjust(bottom=0.2)

plt.plot(x, ndvi, 'ko-', linewidth=1, markersize=5)
plt.plot(x, evi, 'b+--',linewidth=1, markersize=4)
tick_pos = np.arange(tick_step-1, 1000, tick_step)
tick_lables = x_labels[tick_pos]
# You can specify a rotation for the tick labels in degrees or with keywords.
plt.xticks(tick_pos, tick_lables, rotation=45)
plt.xlim(xlim_min, xlim_max)


plt.ylabel("Area(km^2)")
plt.xlabel("Seanonal mesian NDVI")

plt.legend(('NDVI Median Extent', 'EVI Median Extent'), loc='upper left')

# show up the figure in popup window or gui console
if show_enable:
    plt.show()


# plt.savefig(output_path, dpi=dpi)
fig.savefig(output_path)
    
# explicitly clean up the memory.
plt.close()

