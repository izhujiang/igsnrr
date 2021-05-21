# from datetime import datetime

import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt


from enum import Enum


class ModelType(Enum):
    JEKEL_PWLF = "jekel_pwlf_PiecewiseLinFit"
    IGSNRR_PWLFM = "igsnrr_pwlfm_PieceWiseLinearFitModel"


class PieceWiseLinearRegressionContext:
    def __init__(
            self,
            recordNumber,
            minSegmentCount=1,
            maxSegmentCount=4,
            minSegmentLength=1,
            ceofDiffEpsilon=0.00001,
            ceofThreshold=0.99,
            debugLevel=0, **kwargs):

        self.N = recordNumber

        self.minSegmentCount = minSegmentCount
        self.maxSegmentCount = maxSegmentCount
        self.minSegmentLength = minSegmentLength
        self.threshold = ceofThreshold
        self.epsilon = ceofDiffEpsilon

        # default: to test all possibility of potential breaks.
        # [t[0], maxFirstBreak]: valid scope for first potential breaks.
        # [minLastBreak, t[-1]]: valid scope for last potential breaks.
        # if maxFirstBreak is None:
        #     self.maxFirstBreak = self.N - 2
        # else:
        #     self.maxFirstBreak = maxFirstBreak
        # if minLastBreak is None:
        #     self.minLastBreak = 1
        # else:
        #     self.minLastBreak = minLastBreak

        self.debug = debugLevel


# https://github.com/cjekel/piecewise_linear_fit_py
class PieceWiseLinearResult:
    def __init__(
            self,
            corcoef,
            regcoefs,
            breaks,
            generalCorcoef,
            generalPvalue,
            psCorcoefs,
            psPvalues,
            yPred):
        self.corcoef = corcoef
        self.regcoefs = regcoefs
        self.breaks = breaks
        self.generalCorcoef = generalCorcoef
        self.generalPvalue = generalPvalue
        self.psCorcoefs = psCorcoefs
        self.psPvalues = psPvalues
        self.yPred = yPred


def doPieceWise(model, x, y, ctx):
    minSeg = ctx.minSegmentCount
    maxSeg = ctx.maxSegmentCount

    crs = [0] * (maxSeg + 1)  # for storing max correlation coefficient at M
    pvs = [0] * (maxSeg + 1)   # for storing p-value for coefficient at M
    rrs = [[]] * (maxSeg + 1)  # for storing max regression coefficient at M
    # for storing predictions with max correlation coefficient at M
    yps = [[]] * (maxSeg + 1)
    ips = [[]] * (maxSeg + 1)  # for storing inflection points at M

    for M in range(minSeg, maxSeg+1):
        print("fit the data for {0} line segments".format(M))

        model.fit(M, minSegmentLength=ctx.minSegmentLength)
        # fitfast(self, n_segments, pop=2, bounds=None, \*\*kwargs)
        rrs[M] = model.beta
        ips[M] = model.fit_breaks.round(decimals=1)

        # predict for the determined points
        yPred = model.predict(x)
        yps[M] = yPred

        crs[M], pvs[M] = stats.pearsonr(y, yPred)
        # print(M, crs[M])
        # stop iterating by following condition:
        # 1. when max corrcoef is close to 1 (over threshold)
        sc = M
        if abs(crs[M]) > ctx.threshold:
            break
        # 2. when corrcoef varies small enough
        if abs(crs[M] - crs[M - 1]) < ctx.epsilon:
            sc = M - 1
            break

    # ip = ips[sc].round(decimals=1)
    ip = ips[sc]
    r_pw, p_values_pw = calculateCeofsByPiece(x, y, yps[sc], ip)
    pwRes = PieceWiseLinearResult(
            crs[sc],
            rrs[sc],
            ips[sc],
            crs[sc],
            pvs[sc],
            r_pw,
            p_values_pw,
            yps[sc])

    return pwRes


# calclate Corrceof piece by piece
# cc: [x[0], c1, c2, ... x[-1]]
def calculateCeofsByPiece(x, y, yp, cc):
    M = len(cc) - 1

    rs = [0] * M
    p_values = [0] * M

    p0 = x[0]
    for i in range(0, M):
        p1 = cc[i+1]
        indexs = np.logical_and(x >= p0, x <= p1)
        if len(x[indexs]) < 2:
            print(cc)
            print("skipping p0-p1:", p0, p1)
            continue
        # print("p0-p1:",p0, p1)
        # print("x:", x[indexs])
        # print("y:", y[indexs])
        rs[i], p_values[i] = stats.pearsonr(yp[indexs], y[indexs])

        p0 = p1

    return rs, p_values


def exportResult(filepath, pwResArr, df):
    msgs = []
    for item in pwResArr:
        msg = "variable: {0}\n".format(item["name"])
        msgs.append(msg)
        psRes = item["value"]
        msg = "break points: {0}\n".format(psRes.breaks)
        msgs.append(msg)
        msg = "reg_coef: {0}\n".format(psRes.regcoefs)
        msgs.append(msg)
        msg = "general correlation coefficient: {0}\n".format(
                psRes.generalCorcoef)
        msgs.append(msg)
        msg = "general correlation p_values : {0}\n".format(
                psRes.generalPvalue)
        msgs.append(msg)
        msg = "cor_coef_piecewise: {0}\n".format(psRes.psCorcoefs)
        msgs.append(msg)
        msg = "p_values_piecewise: {0}\n".format(psRes.psPvalues)
        msgs.append(msg)
        msgs.append("\n")
    # for msg in msgs:
    #     print(msg)
    with open(filepath, "w") as fo:
        fo.writelines(msgs)

    filepath = filepath.replace(".", ".det.")

    df.to_csv(filepath, sep="\t", index=False, float_format='%10.6f')


def exportImage(model, x, y, breaks, imgPath, showImg=False):
    model.fit_with_breaks(breaks)
    xHat = np.linspace(min(x), max(x), num=1000)
    yHat = model.predict(xHat)

    plt.figure()
    plt.plot(x, y, 'o')
    plt.plot(xHat, yHat, '-')

    plt.savefig(imgPath, dpi=150)
    if showImg:
        plt.show()


if __name__ == "__main__":
    # using_model = ModelType.JEKEL_PWLF
    # or
    using_model = ModelType.IGSNRR_PWLFM

    if using_model == ModelType.JEKEL_PWLF:
        import pwlf
    else:
        import pwlfm

    input_filepath = "/Users/hurricane/share/data.txt"
    df = pd.read_csv(input_filepath, sep='\t')

    nrow, ncol = df.shape
    da = df.to_numpy()
    ctx = PieceWiseLinearRegressionContext(
        recordNumber=nrow,
        minSegmentCount=1,
        maxSegmentCount=4,
        minSegmentLength=3,
        ceofThreshold=0.99,
        ceofDiffEpsilon=0.0000001,
        debugLevel=0,
    )

    x = da[:, 0]
    xName = df.columns[0]
    dfRes = pd.DataFrame(data={
        xName: x})
    pwResArr = [None] * (ncol-1)
    for j in range(1, ncol):
        y = da[:, j]
        yName = df.columns[j]
        yNamePred = df.columns[j] + "_PRED"

        # initialize piecewise linear fit with your x and y data
        if using_model == ModelType.JEKEL_PWLF:
            model = pwlf.PiecewiseLinFit(x, y)
        else:
            model = pwlfm.PieceWiseLinearFitModel(x, y)

        pwRes = doPieceWise(model, x, y, ctx)
        pwResArr[j-1] = {"name": yName, "value": pwRes}
        dfRes[yName] = y
        dfRes[yNamePred] = pwRes.yPred

        imgPath = input_filepath.replace(".txt", "_res_{0}.png".format(yName))
        exportImage(model, x, y, pwRes.breaks, imgPath)

    reuslt_filepath = input_filepath.replace(".", "_res.")
    dfRes = dfRes.convert_dtypes()
    exportResult(reuslt_filepath, pwResArr, dfRes)
