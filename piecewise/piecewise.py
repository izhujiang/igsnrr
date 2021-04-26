import math
# from datetime import timedelta, datetime
from itertools import combinations
from datetime import datetime

import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn import linear_model
import matplotlib.pyplot as plt

# https://zhuanlan.zhihu.com/p/37605060
# https://realpython.com/numpy-scipy-pandas-correlation-python/

# PieceWiseLinearRegressionContext, options for PieceWiseLinearRegression
class PieceWiseLinearRegressionContext:
    def __init__(
            self,
            recordNumber,
            minSegmentCount=1,
            maxSegmentCount=5,
            maxFirstInflection=None,
            minLastInflection=None,
            ceofDiffEpsilon=0.00001,
            ceofThreshold=0.99,
            rollingWinSize=5,
            fixedPointRate=0.3,
            numPotentialInflection=15,
            debugLevel=0):

        self.N = recordNumber

        self.minSegmentCount = minSegmentCount
        self.maxSegmentCount = maxSegmentCount

        self.epsilon = ceofDiffEpsilon
        self.threshold = ceofThreshold

        # default: to test all possibility of potential Inflections.
        # [t[0], maxFirstInflection]: valid scope for first potential Inflections.
        # [minLatInflection(2), t[-1]]: valid scope for last potential Inflections.
        if maxFirstInflection is None:
            self.maxFirstInflection = self.N - 2
        else:
            self.maxFirstInflection = maxFirstInflection
        if minLastInflection is None:
            self.minLastInflection = 1
        else:
            self.minLastInflection = minLastInflection

        self.rollingWinSize = rollingWinSize
        self.fixedPointRate = fixedPointRate

        self.numPotentialInflection = numPotentialInflection

        self.debug = debugLevel

class PieceWiseLinearResult:
    def __init__(
            self,
            corcoef, 
            regcoefs, 
            inflectionPoints, 
            generalCorcoef,
            generalPvalue, 
            psCorcoefs, 
            psPvalues,
            yPred):
        self.corcoef = corcoef
        self.regcoefs = regcoefs
        self.inflectionPoints = inflectionPoints
        self.generalCorcoef = generalCorcoef
        self.generalPvalue = generalPvalue
        self.psCorcoefs = psCorcoefs
        self.psPvalues = psPvalues
        self.yPred = yPred
   

class PieceWiseLinearRegression:
    def __init__(
            self,
            t, y, potentialInflectionPoints,
            context):
        """
        t, y with shape of (N, 1)
        """
        self.y = y
        self.t = t
        self.potentialInflectionPoints = potentialInflectionPoints
        self.ctx = context

    def fit(self):
        # N = len(self.t)
        epsilon = ctx.epsilon
        threshold = ctx.threshold
        # M segments, c[1, ..., M-1]
        minSegCnt = ctx.minSegmentCount
        maxSegCnt = ctx.maxSegmentCount
        isDebug = ctx.debug

        M = maxSegCnt
        cr = [0] * (M + 1)  # for storing max correlation coefficient at M
        rr = [[]] * (M + 1)  # for storing max regression coefficient at M
        yps = [[]] * (M + 1)  # for storing predictions with max correlation coefficient at M
        ips = [[]] * (M + 1)  # for storing inflection points at M
        ts = [0] * (M + 1)  # for storing time comsming at M
        sc = M  # for storing section count

        cr[0] = - math.inf
        t1 = datetime.now()

        
        for M in range(minSegCnt, maxSegCnt + 1):
            cr[M], rr[M], ips[M], yps[M] = self.MaxCorrcoef(M)
            sc = M
            # level 1 debug for time and max corrcoef at M segments.
            if isDebug > 0:
                print("current M segments: {0}".format(M))
                t2 = datetime.now()
                ts[M] = (t2-t1).seconds
                t2 = t1
                print("{0} pieces, comsuming {1} secends:".format(M, ts[M]))
                print("max corrcoef {0} & breaks at {1}:\n".format(cr[M], ips[M]))


            # stop iterating by following condition:
            # 1. when max corrcoef is close to 1 (over threshold)
            if abs(cr[M]) > threshold:
                if isDebug > 0:
                    print("{0} piecewise and split points:{1} max corrcoef {2}.\
                            \n".format(M, ips[M], cr[M]))
                
                r_general, p_values_general, r_pw, p_values_pw = self.calculateCeofsByPiece(yps[M], ips[M])
                # print("abs of cor_coefs: ", cor_coefs)
                if min(r_pw) > threshold:
                    sc = M
                    break
            # 2. when corrcoef varies small enough
            if abs(cr[M] - cr[M - 1]) < epsilon:
                if isDebug > 0:
                    print("{0} piecewise and split points:{1} with max corrcoef \
                            {2}:{3}. \n".format(M-1, ips[M-1], cr[M-1], cr[M]))
                # return cr[M-1], c[M-1]
                sc = M - 1
                break
        r_general, p_values_general, r_pw, p_values_pw  = self.calculateCeofsByPiece(yps[sc], ips[sc])
        pwRes = PieceWiseLinearResult(cr[sc], 
            rr[sc], 
            ips[sc], 
            r_general, 
            p_values_general, 
            r_pw, 
            p_values_pw,
            yps[sc])
        return pwRes

    def MaxCorrcoef(self, M):
        max_c = None
        max_cor_coef = -1
        max_reg_coefs = None
        predictions = []

        if M == 1:
            max_cor_ceof, max_reg_coefs, predictions = self.calculateMultipleLinearRegression([])
            return max_cor_ceof, max_reg_coefs , [], predictions

        cs = combinations(self.potentialInflectionPoints, M - 1)

        maxFirstInflection = self.ctx.maxFirstInflection
        minLastInflection = self.ctx.minLastInflection
        isDebug = self.ctx.debug
        # index = 0
        for c in cs:
            if (c[0] == self.t[0] 
                or c[0] > maxFirstInflection
                or c[-1] < minLastInflection
                or c[-1] == self.t[ctx.N-1]):
                continue
            cor_coef,reg_coef, tmp_predictions = self.calculateMultipleLinearRegression(c)
            
            if cor_coef > max_cor_coef:
                max_cor_coef = cor_coef
                max_reg_coefs = reg_coef
                predictions = tmp_predictions
                max_c = c
                # debug level 2 for print internal max coef at specific M
                if isDebug > 1:
                    print(c, cor_coef)
                    print(max_reg_coefs)

        return max_cor_coef, max_reg_coefs, max_c, predictions

    def calculateMultipleLinearRegression(self, c):
        # M = len(c) + 1
        N = len(self.y)

        cor_ceof = None
        reg_ceofs = None
        
        cc = np.concatenate((self.t[:1], np.array(c), self.t[-1:]), axis=0)
        if self.ctx.debug > 0:
            print(cc)

        X = self.setupVirtualX(self.t, cc)
        Y = self.y.reshape((N, 1))
        
        lm = linear_model.LinearRegression()
        lm.fit(X, Y)
        reg_ceofs = lm.coef_.flatten()
        predictions = lm.predict(X).flatten()
        cor_ceof = np.corrcoef(predictions, self.y)

        return cor_ceof[0, 1], reg_ceofs, predictions

    
    # T[0, 1, ..., N-1, N] 
    # C[0, 1, ..., M-1, M] 
    def setupVirtualX(self, T, C):
        # N = len(t)
        M = len(C)
        TT = T.reshape((-1, 1))
        # print(TT)

        def vFunc(vArr):
            t = vArr[0]
            x = np.zeros(M)
            x[0] = 1
            for j in range(1, M): # test where is t located [ *, C[j-1], *, C[j], *]
                if t > C[j]:
                    x[j] = C[j] - C[j-1]
                elif t < C[j -1]:
                    break
                else:  # C[j-1] <= t <= C[j]
                    x[j] = t - C[j-1]
            return x
            
        X = np.apply_along_axis(vFunc, 1, TT)
        # print(C, X)

        return X[:,1:]

    # calclate Corrceof piece by piece
    def calculateCeofsByPiece(self, ps, c):
        M = len(c) + 1

        rs = [0] * M
        p_values = [0] * M
        cc = np.concatenate((np.array(c), self.t[-1:]), axis=0)
        # print("cc:", cc)
        # print("t: ", self.t)
        # print("y: ", self.y)
        # print("yp: ", ps)
        

        p0 = self.t[:1]
        # print("calculateCeofsByPiece:", cc, ps)
        for i in range(M):
            p1 = cc[i]
            indexs = np.logical_and(self.t >= p0 , self.t <= p1)
            rs[i], p_values[i] = stats.pearsonr(ps[indexs], self.y[indexs])
            # print("piecewise {0}.".format(self.t[indexs]))
            # print("y: {0}, yp:{1}.".format(self.y[indexs], ps[indexs]))
            # print("corrcoef: {0}, p_value:{1}.\n".format(rs[i], p_values[i]))
            p0 = p1

        r_tatal, p_values_tatal = stats.pearsonr(ps, self.y)

        return r_tatal, p_values_tatal, rs, p_values

# input:df -- pandas.Dataframe, include [T, Y]
# caution: t -- [1,2...N],
def doPieceWise(df, ctx):
    if ctx.numPotentialInflection in [None, 0, ctx.N]:
        potentialInflections = df['T'][1:-1].to_numpy()
        
    else:
        doMovingAverages(df, ctx)
        nlargest_row = df.nlargest(ctx.numPotentialInflection, 'Y_GRD')
        df['NLG_GRD'] = nlargest_row['Y_AVG']
        nlargest_day = np.sort(nlargest_row['T'].to_numpy())
        potentialInflections = nlargest_day

    if ctx.debug:
        print("-----------------------------------------")
        print("potential inflection points", potentialInflections)

    t = df['T'].to_numpy()
    y = df['Y'].to_numpy()
    pwlr = PieceWiseLinearRegression(t, y, potentialInflections, ctx)
    pwRes = pwlr.fit()
    df.loc[:, ['Y_PRED']] = pwRes.yPred
    
    return pwRes

# helper functions
# 
def doMovingAverages(df, ctx):
    df['Y_AVG'] = df['Y'].rolling(
            window=ctx.rollingWinSize, min_periods=1, center=True).mean()
    (row, _) = df.shape

    numFixPoint = int(row * ctx.fixedPointRate)
    df['Y_DELTA'] = abs(df['Y_AVG'] - df['Y'])
    reset_threshold = df['Y_DELTA'].nlargest(numFixPoint).min()

    df.loc[df['Y_DELTA'] >= reset_threshold, 'Y_AVG'] = df['Y']
    y_avg = df['Y_AVG'].to_numpy()
    y_avg_grd = np.abs(np.gradient(np.gradient(y_avg)))
    df['Y_GRD'] = y_avg_grd
    # print(df)

# dispaly df with T, Y, Y_PRED fields
def doDisplay(df):
    # the sie of figure, unit: inch
    FIG_SIZE = (16, 12)

    # Plot outputs
    (cn_row, cn_col) = df.shape
    x = df['T']
    y = df['Y']
    
    y_pred = df['Y_PRED']
    plt.figure(figsize=FIG_SIZE)
    plt.scatter(y, y_pred)

    plt.figure(figsize=FIG_SIZE)
   
    # plt.plot(x, ndvi, color='blue', linewidth=1)
    plt.grid(b=True, which='both')
    # grid(b=None, which='major', axis='both', **kwargs)[source]¶
    y_line, = plt.plot(x, y, color='red', label="Y", linewidth=1)
    y_pred_line, = plt.plot(
            x, y_pred, color='blue', label="Y_PRED", linewidth=1)
    plt.scatter(x, y, marker="D")
    plt.scatter(x, y_pred, marker='o')

    handles = [y_line,  y_pred_line]

    plt.legend(handles=handles, loc='upper right')

def exportResult(filepath, psRes, df):
    msgs = []
    msg = "max_cor_coef: {0}\n".format(psRes.corcoef)
    msgs.append(msg)
    msg = "reg_coef: {0}\n".format(psRes.regcoefs)
    msgs.append(msg)
    msg = "inflection points: {0}\n".format(psRes.inflectionPoints)
    msgs.append(msg)
    msg = "general correlation coefficient: {0}\n".format(psRes.generalCorcoef)
    msgs.append(msg)
    msg = "eneral correlation p_values : {0}\n".format(psRes.generalPvalue)
    msgs.append(msg)
    msg = "cor_coef_piecewise: {0}\n".format(psRes.psCorcoefs)
    msgs.append(msg)
    msg = "p_values_piecewise: {0}\n".format(psRes.psPvalues)
    msgs.append(msg)


    with open(filepath, "w") as fo:
        fo.writelines(msgs)
    filepath = filepath.replace(".", ".det.")
    df.to_csv(filepath, sep="\t", index=False, float_format='%10.6f')

if __name__ == "__main__":
    #
    DATA_LOADFROM_FILE = True
    ENABLE_DISPLAY = True

    # ------------------------------------------------
    # load data
    if DATA_LOADFROM_FILE:
        input_filepath = "/Users/hurricane/share/data.txt"
        df = pd.read_csv(input_filepath, sep='\t')

    else:
        t = np.arange(0, 20)
        y = np.zeros(20)
        SD = 40
        for i in range(0, 10):
           y[i] = 1083 + np.random.randn() * SD
        for i in range(10, 20):
            y[i] = 1580 + np.random.randn() * SD
        print(y)
        data = {'T': t, 'Y': y}
        df = pd.DataFrame.from_dict(data)
    
    nrow, ncol = df.shape
#        if nrow < 15:
#            numPotentials = nrow
#        elif nrow < 30:
#            numPotentials = 15 + int((nrow - 15)/2)
#        else:
#            numPotentials = min(50, 30 + int(nrow-30)/2)
    
    #------------------
    ctx = PieceWiseLinearRegressionContext(
        recordNumber=nrow,
        minSegmentCount=4,
        maxSegmentCount=4,
        maxFirstInflection=2018,
        minLastInflection=2001,
        ceofThreshold=0.99,
        ceofDiffEpsilon=0.0000001,
        rollingWinSize=11,
        fixedPointRate=0.4,
        numPotentialInflection=nrow,
        debugLevel=0,
    )


    org_df = df
    # ncol = 2
    for i in range(1, ncol):
        df = org_df.iloc[:, [0, i]]
        tName = df.columns[0]
        yName = df.columns[1]
        
        df.columns = ["T", "Y"]
        pwRes = doPieceWise(df, ctx)
        # doCorrelationAndTest(df, cp, max_cor_coef)

        if ENABLE_DISPLAY:
            doDisplay(df)

        df.columns = [tName, yName, yName + "-PRED"] 
        if ctx.debug > 0:
            print(df)

        reuslt_filepath = input_filepath.replace(".","_res_{0}.".format(yName))
        exportResult(reuslt_filepath, pwRes, df)