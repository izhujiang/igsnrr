import numpy as np

def initResultStorage(shape, nodata):
    bands_data = {
        'max': np.full(shape, nodata, np.float32),
    }
    bands_desc = {
        'max': "maximum vale",
    }

    return bands_data, bands_desc 

def analyzeSinglePoint(x):
    res = {
        'max': x.max()
    }

    return res