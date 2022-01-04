import numpy as np
import statsmodels.api as sm

def initResultStorage(shape, nodata):
    bands_data = {
        'b0': np.full(shape, nodata, np.float32),
        'b1': np.full(shape, nodata, np.float32),
        'r2': np.full(shape, nodata, np.float32),
        'p0': np.full(shape, nodata, np.float32),
        'p1': np.full(shape, nodata, np.float32),
        'f': np.full(shape, nodata, np.float32),
        't0': np.full(shape, nodata, np.float32),
        't1': np.full(shape, nodata, np.float32),
    }
    bands_desc = {
        'b0': "coef b0",
        'b1': "coef b1",
        'r2': "R-squared",
        'p0': "P>|t| (P0)",
        'p1': "P>|t| (P1)",
        'f': "F-statistic",
        't0': "tValue t0",
        't1': "tValue t1",
    }

    return bands_data, bands_desc 

def analyzeSinglePoint(x, y):
    x = sm.add_constant(x)
    model = sm.OLS(y, x)
    results = model.fit()
    # print(x, results.summary())

    res = {
        'b0': results.params[0],
        'b1': results.params[1],
        'r2': results.rsquared,
        'p0': results.pvalues[0],
        'p1': results.pvalues[1],
        'f': results.fvalue,
        't0': results.tvalues[0],
        't1': results.tvalues[1],
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
    # analyzeSinglePoint(x, y, AnalysisMethood.MANNKENDALL)
