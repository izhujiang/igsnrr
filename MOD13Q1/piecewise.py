# -*- coding: utf-8 -*-
import math
# from datetime import timedelta, datetime
from itertools import combinations
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn import linear_model
import matplotlib.pyplot as plt

# https://zhuanlan.zhihu.com/p/37605060

# D1-Object: inde between [1,M], used by setupVirtualVairableX
class D1Object:
    # c: numpy.array
    def __init__(self, c):
        self.c = c

    def valueAt(self, k):
        return self.c[k-1]

    def setValueAt(self, i, v):
        self.x[i - 1] = v

    def toString(self):
        return ','.join(str(x) for x in self.c)  # '0,3,5'


# D2-Object: inde between [1, 1] - [N, M], used by setupVirtualVairableX
class D2Object:
    # x: 2-D numpy.array
    def __init__(self, N, M):
        self.x_data = np.empty(shape=(N, M))

    def valueAt(self, i, j):
        return self.x_data[i - 1, j - 1]

    def setValueAt(self, i, j, v):
        self.x_data[i - 1, j - 1] = v

    def to_numpy(self):
        # row, _ = self.x_data.shape
        # for i in range(row):
        #     print(self.x_data[i, :])
        return self.x_data


# PieceWiseLinearRegressionContext, options for PieceWiseLinearRegression
class PieceWiseLinearRegressionContext:
    def __init__(
            self,
            recordNumber,
            minSegmentCount=1,
            maxSegmentCount=5,
            maxFirstInflection=None,
            minLastInflection=2,
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
        # [0, maxFirstInflection]: valid scope for first potential Inflections.
        # [minLatInflection, nrow]: valid scope for last potential Inflections.
        if maxFirstInflection is None:
            self.maxFirstInflection = self.N - 1
        else:
            self.maxFirstInflection = maxFirstInflection
        self.minLastInflection = minLastInflection

        self.rollingWinSize = rollingWinSize
        self.fixedPointRate = fixedPointRate

        self.numPotentialInflection = numPotentialInflection

        self.debug = debugLevel


class PieceWiseLinearRegression:
    def __init__(
            self,
            t, y, potentialInflection,
            pieceWiseLinearRegressionContext):
        self.y = y
        self.t = t
        self.pc = potentialInflection
        self.ctx = pieceWiseLinearRegressionContext

    def findSections(self):
        # N = len(self.t)
        epsilon = self.ctx.epsilon
        threshold = self.ctx.threshold

        M = (len(self.pc) + 1)
        r = [0] * (M + 1)  # for storing max correlation coefficient at M
        rr = [0] * (M + 1)  # for storing max regression coefficient at M
        c = [[]] * (M + 1)  # for storing inflection points at M
        ts = [0] * (M + 1)  # for storing time comsming at M
        sc = M  # for storing section count

        r[0] = - math.inf
        t1 = datetime.now()

        # M segments, c[1, ..., M-1]
        minSegCnt = self.ctx.minSegmentCount
        maxSegCnt = self.ctx.maxSegmentCount
        isDebug = self.ctx.debug
        for M in range(minSegCnt, maxSegCnt + 1):
            r[M], rr[M], c[M] = self.MaxCorrcoef(M)
            sc = M
            # level 1 debug for time and max corrcoef at M segments.
            if isDebug > 0:
                print("current M segments: {0}".format(M))
                t2 = datetime.now()
                ts[M] = (t2-t1).seconds
                t2 = t1
                print("{0} pieces, comsuming {1} secends:".format(M, ts[M]))
                print("max corrcoef {0} & breaks at {1}:\n".format(r[M], c[M]))

            # stop iterator by following condition
            # when max corrcoef is close to 1 (over threshold)
            if abs(r[M]) > threshold:
                if isDebug > 0:
                    print("{0} piecewise and split points:{1} max corrcoef {2}.\
                            \n".format(M, c[M], r[M]))
                # return r[M], c[M]
                cor_coefs = self.calculateCorrceofByPiece(c[M])
                print("abs of cor_coefs: ", cor_coefs)
                if min(cor_coefs) > threshold:
                    sc = M
                    break
            # when corrcoef varies small enough during the iterate
            if abs(r[M] - r[M - 1]) < epsilon:
                if isDebug > 0:
                    print("{0} piecewise and split points:{1} with max corrcoef \
                            {2}:{3}. \n".format(M-1, c[M-1], r[M-1], r[M]))
                # return r[M-1], c[M-1]
                sc = M - 1
                break
        return r[sc], rr[sc], c[sc]

    def MaxCorrcoef(self, M):
        max_c = None
        max_cor_coef = -1
        max_reg_coef = None

        if M == 1:
            max_cor_ceof, max_reg_coef = self.calculateCorrceof([])
            return max_cor_ceof, max_reg_coef , ()

        cs = combinations(self.pc, M - 1)

        maxFirstInflection = self.ctx.maxFirstInflection
        minLastInflection = self.ctx.minLastInflection
        isDebug = self.ctx.debug
        # index = 0
        for c in cs:
            if M >= 4 and (
                    c[0] > maxFirstInflection
                    or c[-1] < minLastInflection):
                continue
            # print(c)
            # print(c, index)
            # index += 1

            # t1 = datetime.now()
            cor_coef,reg_coef = self.calculateCorrceof(c)
            # t2 = datetime.now()

            # print("calculateCorrceof consuming ", t2 - t1)

            if cor_coef > max_cor_coef:
                max_cor_coef = cor_coef
                max_reg_coef = reg_coef
                max_c = c
                # debug level 2 for print internal max coef at specific M
                if isDebug > 1:
                    print(c, cor_coef)
                    print(max_reg_coef)

        return max_cor_coef, max_reg_coef, max_c

    def calculateCorrceof(self, c):
        M = len(c) + 1
        N = len(self.y)

        cor_ceof = None
        reg_ceof = None

        if M == 1:
            # X = self.t.reshape((N, 1))
            # Y = self.y.reshape((N, 1))
            cor_ceof = np.corrcoef(self.t, self.y)
            X = self.t.reshape((N, 1))
            Y = self.y.reshape((N, 1))
            lm = linear_model.LinearRegression()
            lm.fit(X, Y)
            reg_ceof = lm.coef_[0]
            # print("1 segement with correlation coefficient", cor_ceof)
            # print("1 segement with regression coefficient", reg_ceof)

        else:
            cc = np.concatenate((np.array(c), self.t[-1:]), axis=0)
            # print(cc)
            CC = D1Object(cc)

            XX = self.setupVirtualX(N, M, CC)
            X = XX.to_numpy()
            Y = self.y.reshape((N, 1))

            # print(X, Y)
            # with sklearnk
            lm = linear_model.LinearRegression()
            lm.fit(X, Y)
            reg_ceof = lm.coef_[0]
            predictions = lm.predict(X).reshape((1, N))
            cor_ceof = np.corrcoef(predictions, self.y)

            # print(c)
            # print(M, " segement with correlation coefficient")
            # print(cor_ceof)
            # print(M, " segement with regression coefficient")
            # print(reg_ceof)
            # score = lm.score(X, Y)

        return cor_ceof[0, 1], reg_ceof

    # N Seriels
    # M segments
    # c[1, ..., M-1]
    def setupVirtualX(self, N, M, C):
        v = None
        X = D2Object(N, M)

        # print(C.toString(), '[', i, j, ']')
        for i in range(1, N+1):
            for j in range(1, M+1):
                if j == 1:
                    if(i <= C.valueAt(1)):
                        v = i
                    else:
                        v = C.valueAt(1)
                else:
                    if i <= C.valueAt(j - 1):
                        v = 0
                    elif i > C.valueAt(j):
                        v = C.valueAt(j) - C.valueAt(j-1)
                    else:
                        v = i - C.valueAt(j - 1)

                X.setValueAt(i, j, v)
        # print(N, M, C, X)

        return X

    # calclate Corrceof piece by piece
    def calculateCorrceofByPiece(self, c):
        M = len(c) + 1

        cor_ceofs = [0] * M
        cc = np.concatenate((np.array(c), self.t[-1:]), axis=0)

        p0 = 1
        # print(c)
        for i in range(M):
            p1 = cc[i]
            # print(self.t[p0-1:p1])
            cor_ceofs[i] = abs(np.corrcoef(self.t[p0-1:p1], self.y[p0-1:p1])[0,1])

            p0 = p1

        return cor_ceofs

# -------- Helper functions and classes -------------------
class Output:
    def __init__(self, filepath):
        self.fo = open(filepath, "w")

    def print(self, msg):
        print(msg)  # output to console
        self.fo.writelines(["{0}\n".format(msg)])   # output to file

    def flush(self):
        self.fo.close()


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

# input:df -- pandas.Dataframe, include [T, Y]
# caution: t -- [1,2...N],
def doPieceWise(df, ctx):
    min = df['T'].min()
    if min != 1:
        df['T'] = df['T'] - (min -1)
    doMovingAverages(df, ctx)

    nlargest_row = df.nlargest(ctx.numPotentialInflection, 'Y_GRD')
    df['NLG_GRD'] = nlargest_row['Y_AVG']
    nlargest_day = np.sort(nlargest_row['T'].to_numpy())

    if ctx.debug:
        print("-----------------------------------------")
        print("potential inflection points", nlargest_day)

    t = df['T'].to_numpy()
    y = df['Y'].to_numpy()
    # print(t, y, nlargest_day)

    pwlr = PieceWiseLinearRegression(
       t, y, nlargest_day, ctx)
    # cp - connected points with max coef.
    max_cor_coef, max_reg_coef, cp = pwlr.findSections()
    # print(max_cor_coef, max_reg_coef, cp)
    return max_cor_coef, max_reg_coef, cp


def listPieceWiseByInflection(
        df, rolling_win_size,
        minNumPotentialInflection=5,
        maxNumPotentialInflection=50,
        output=None):
    t1 = datetime.now()
    step = 2

    for numInf in range(
            minNumPotentialInflection, maxNumPotentialInflection+1, step):
        max_cor_coef, max_reg_coef, cp = doPieceWise(df, numInf)
        if output is not None:
            output.print(
                    "{0}\t{1}\t{2}\t{3}\t{4}".format(
                        rolling_win_size, numInf, len(cp) + 1, max_cor_coef,max_reg_coef,cp))

    t2 = datetime.now()
    print("time comsuming for loop ({0},{1}:{2}): {3} seconds".format(
        minNumPotentialInflection, maxNumPotentialInflection, step,
        (t2-t1).seconds))


def doSeperateLinearRegression(df, cp):
    (cn_row, cn_col) = df.shape
    t = df['T'].to_numpy()
    y = df['Y'].to_numpy()
    c = cp + (cn_row,)

    start = 0
    preds = np.empty((1, 0))
    for end in c:
        X = t[start: end].reshape(-1, 1)
        Y = y[start: end]
        # print(X, Y)

        lm = linear_model.LinearRegression()
        lm.fit(X, Y)

        # score = lm.score(X,Y)
        # print(score)
        predictions = lm.predict(X)
        preds = np.append(preds, predictions)
        start = end

    df['Y_PRED'] = preds


# df: X, Y, Y_AVG, Y_GRD, NLG_GRD,
def doDisplay(df):
    # the sie of figure, unit: inch
    FIG_SIZE = (16, 12)

    # Plot outputs
    (cn_row, cn_col) = df.shape
    x = df['T']
    y = df['Y']
    nlg = df['NLG_GRD']

    y_avg = df['Y_AVG']
    y_grd = df['Y_GRD']
    y_pred = df['Y_PRED']

    plt.figure(figsize=FIG_SIZE)
    # plt.xlim(left=0, right=cn_row)
    # plt.ylim(bottom=0, top=0.4)

    plt.scatter(x, nlg,  color='black')
    annos = df[pd.notna(df['NLG_GRD'])][['T', 'NLG_GRD']]
    # print(annos)

    old_x = old_y = 1e9  # make an impossibly large initial offset
    thresh = 2  # make a distance threshold
    for row in annos.itertuples():
        px, py = row[1], row[2]
        label = "{}".format(px)

        # calculate distance
        d = ((px-old_x)**2+(py-old_y)**2)**(.5)
        # if distance less than thresh then flip the arrow
        flip = 1
        # print(d)
        if d < thresh:
            flip = -2

        plt.annotate(
            label,
            xy=(px, py), xytext=(-20*flip, 5*flip),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        old_x = px
        old_y = py

    # plt.plot(x, ndvi, color='blue', linewidth=1)
    plt.grid(b=True, which='both')
    # grid(b=None, which='major', axis='both', **kwargs)[source]¶
    y_line, = plt.plot(x, y, color='red', label="Y", linewidth=1)
    y_avg_line, = plt.plot(x, y_avg, color='cyan', label="Y_AVG", linewidth=1)
    y_grd_line, = plt.plot(x, y_grd, color='green', label="Y_GRD", linewidth=1)
    y_pred_line, = plt.plot(
            x, y_pred, color='blue', label="Y_PRED", linewidth=1)
    plt.scatter(x, y, marker="D")

    handles = [y_line, y_avg_line, y_grd_line, y_pred_line]

    plt.legend(handles=handles, loc='upper right')


if __name__ == "__main__":
    #
    DATA_LOADFROM_FILE = True

    ENABLE_DISPLAY = True
    SHOW_ALL_INFLECTION = False

    DEBUG_ENABLE = False

    # ------------------------------------------------
    # load data
    if DATA_LOADFROM_FILE:
        df = pd.read_csv(
            "/Users/jiangzhu/workspace/igsnrr/data/ndvi/ndvi_2004.txt",
            sep='\t')
        numPotentials = 20
        maxFirstInflection = 151
        minLastInflection = 273
        rollingWinSize = 11
        fixedPointRate = 0.4
        ceofThreshold = 0.95
        ceofDiffEpsilon = 0.0000001
    else:
        t = np.arange(0, 20)
        # y = np.array([
        #    1447, 1580, 2037, 1779.9266, 1398.0007, 1614.4379,
        #    1493.4379, 1580, 1613, 1728.7712, 1630.695, 1516.4379, 1775.1046,
        #    1434.4379, 1383.695, 1720.7784, 1664, 1578.9172, 1711.4103, 1691])

        y = np.zeros(20)
        SD = 40

        # for i in range(0, 20):
        #     y[i] = 1047 + (1583 - 1047) * i / 20 + np.random.randn() * SD

        # for i in range(0, 6):
        #      y[i] = 1047 + (1583 - 1047) * i / 6 + np.random.randn() * SD
        # for i in range(6, 20):
        #     y[i] = 1583 + (1283 - 1583) * (i-6 )/ 14 + np.random.randn() * SD

        # for i in range(6):
        #     y[i] = 1047 + np.random.randn() * SD
        # for i in range(6, 15):
        #     y[i] = 1047 + (1583 - 1047) * (i - 6) / (15 - 6) + np.random.randn() * SD
        # for i in range(15, 20):
        #     y[i] = 1583 + np.random.randn() * SD
        for i in range(0, 10):
           y[i] = 1083 + np.random.randn() * SD
        for i in range(10, 20):
            y[i] = 1580 + np.random.randn() * SD
        print(y)
        data = {'T': t, 'Y': y}
        df = pd.DataFrame.from_dict(data)
        numPotentials = 10
        maxFirstInflection = 19
        minLastInflection = 2
        rollingWinSize = 5
        fixedPointRate = 0.3
        ceofThreshold = 0.9
        ceofDiffEpsilon = 0.00001

    if SHOW_ALL_INFLECTION:
        pass
        # now = datetime.now()
        # log = Output("./coef_" + now.strftime("%Y%m%d%H%M%S") + ".log")
        # for rolling_win_size in range(5, 32, 2):
        #     doMovingAverages(df, rolling_win_size)
        #     listPieceWiseByInflection(df,
        # rolling_win_size=rollingWinSize,
        # minNumPotentialInflection=5,
        #             maxNumPotentialInflection=50, output=log)
        # log.flush()
    else:
        nrow, _ = df.shape
#        if nrow < 15:
#            numPotentials = nrow
#        elif nrow < 30:
#            numPotentials = 15 + int((nrow - 15)/2)
#        else:
#            numPotentials = min(50, 30 + int(nrow-30)/2)
        ctx = PieceWiseLinearRegressionContext(
            recordNumber=nrow,
            minSegmentCount=1,
            maxSegmentCount=5,
            maxFirstInflection=maxFirstInflection,
            minLastInflection=minLastInflection,
            ceofThreshold=ceofThreshold,
            ceofDiffEpsilon=ceofDiffEpsilon,
            rollingWinSize=rollingWinSize,
            fixedPointRate=fixedPointRate,
            numPotentialInflection=numPotentials,
            debugLevel=1,
        )

        t1 = datetime.now()
        max_cor_coef, max_reg_coef, cp = doPieceWise(df, ctx)
        t2 = datetime.now()
        t2 - t1

        print(
            "{0} piecewise and split points:{1} \nmax correlation corrcoef {2}.\n\
regression corrcoef {3} \ncosuming {4}".format(
                len(cp) + 1, cp, max_cor_coef, max_reg_coef, (t2 - t1)))
        if ENABLE_DISPLAY:
            doSeperateLinearRegression(df, cp)
            doDisplay(df)