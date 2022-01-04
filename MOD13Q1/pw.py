import numpy as np
import pwlfm 
import statsmodels.api as sm

def initResultStorage(shape, nodata):
    bands_data = {
        'NS': np.full(shape, nodata, np.float32),
        'ceof': np.full(shape, nodata, np.float32),
        'S1': np.full(shape, nodata, np.float32),
        'S2': np.full(shape, nodata, np.float32),
        'S3': np.full(shape, nodata, np.float32),
        'S4': np.full(shape, nodata, np.float32),
        'b1': np.full(shape, nodata, np.float32),
        'b2': np.full(shape, nodata, np.float32),
        'b3': np.full(shape, nodata, np.float32),
        'b4': np.full(shape, nodata, np.float32),
        'b5': np.full(shape, nodata, np.float32),
        'c1': np.full(shape, nodata, np.float32),
        'c2': np.full(shape, nodata, np.float32),
        'c3': np.full(shape, nodata, np.float32),
        'c4': np.full(shape, nodata, np.float32),
        'c5': np.full(shape, nodata, np.float32),
    }
    bands_desc = {
        'NS': "segements count",
        'ceof': "correlation coefficient",
        'S1': "first segment point",
        'S2': "second segment point",
        'S3': "third segment point",
        'S4': "forth segment point",
        'b1': "first segment slope / regression coefficient",
        'b2': "second segment slope / regression coefficient",
        'b3': "third segment slope / regression coefficient",
        'b4': "forth segment slope / regression coefficient",
        'b5': "fifth segment slope / regression coefficient",
        'c1': "first segment correlation coefficient",
        'c2': "second segment correlation coefficient",
        'c3': "third segment correlation coefficient",
        'c4': "forth segment correlation coefficient",
        'c5': "fifth segment correlation coefficient"
    }

    return bands_data, bands_desc 

ctx = pwlfm.PieceWiseLinearRegressionContext(
    minSegmentCount=1,
    maxSegmentCount=4,
    minSegmentLength=3,
    ceofThreshold=0.90,
    ceofDiffEpsilon=0.000001,
    debugLevel=0,
)

def analyzeSinglePoint(x, y):
    pwRes = pwlfm.DoPieceWise(x, y, ctx)

    # max_cor_coef, max_reg_coef, cp = pw.doPieceWise(df, ctx)

    res = {
        'NS': len(pwRes.breaks) - 1,
        'ceof': pwRes.generalCorcoef,
    }
    for i in range(1, len(pwRes.breaks)):
        res["S{0}".format(i)] = pwRes.breaks[i]
    for i in range(len(pwRes.regcoefs)):
        res["b{0}".format(i+1)] = pwRes.regcoefs[i]
    for i in range(len(pwRes.psCorcoefs)):
        res["c{0}".format(i+1)] = pwRes.psCorcoefs[i]

    return res

if __name__ == "__main__":
    
    x = np.asarray([2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
                   2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021])
    y = np.asarray([276.84527587890625, 358.33203125, 314.0, 62.0, 100.0, 83.0, 415.0, 366.29766845703125,
                    454.0, 372.99871826171875, 137.8452606201172, 344.806884765625, 102.0, 284.2381286621094,
                    243.0, 512.0, 458.0, 349.8360290527344, 48.84526062011719, 140.0, 301.5119323730469, 327.0])
    for i in range(100):
        y  =  y + np.random.randint(5, size=(22))
        res = analyzeSinglePoint(x, y)
        # print(res)