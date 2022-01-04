import numpy as np
import mkt

def initResultStorage(shape, nodata):
    bands_data = {
        'zmk': np.full(shape, nodata, np.float32),
        'ha': np.full(shape, nodata, np.float32),
        'm': np.full(shape, nodata, np.float32),
        'c': np.full(shape, nodata, np.float32),
        'p': np.full(shape, nodata, np.float32),
    }
    bands_desc = {
        'zmk': "the Z-score based on above estimated mean and variance",
        'ha': "result of the statistical test indicating whether \
                or not to accept hte alternative hypothesis ‘Ha’",
        'm': "slope of the linear fit",
        'c': "intercept of the linear fit",
        'p': "p-value of the obtained Z-score statistic",
    }

    return bands_data, bands_desc 

def analyzeSinglePoint(x, y):
     # get the slope, intercept and pvalues from the mklt module
    ALPHA = 0.05
    #        MK : string
    #     result of the statistical test indicating whether or not to accept hte
    #     alternative hypothesis 'Ha'
    # m : scalar, float
    #     slope of the linear fit to the data
    # c : scalar, float
    #     intercept of the linear fit to the data
    # p : scalar, float, greater than zero
    #     p-value of the obtained Z-score statistic for the Mann-Kendall test

    Zmk, MK, m, c, p = mkt.test(x, y, eps=1E-3, alpha=ALPHA, Ha="upordown")

    ha = 1
    if MK.startswith('rej'):
        ha = 0
    # ha = not MK.startswith('reject')
    res = {
        'zmk': Zmk,
        'ha': ha,
        'm': m,
        'c': c,
        'p': p,
    }

    return res

if __name__ == "__main__":
    # for debug sinle point
    x = np.array(list(range(1, 21)))
    y = np.array([
        1447, 1580, 2037, 1779.9266, 1398.0007, 1614.4379,
        1493.4379, 1580, 1613, 1728.7712, 1630.695, 1516.4379,
        1775.1046, 1434.4379, 1383.695, 1720.7784, 1664, 1578.9172,
        1711.4103, 1691])
    res = analyzeSinglePoint(x, y)
    print(res)