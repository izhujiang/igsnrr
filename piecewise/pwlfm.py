# import math
from itertools import combinations
import numpy as np

from sklearn import linear_model

# import matplotlib.pyplot as plt


class PieceWiseLinearFitModel:
    def __init__(
            self,
            x, y):
        """
        x, y with shape of (N, 1)
        """
        self.y = y
        self.t = x
        self.lm = linear_model.LinearRegression()

    def fit(self, n_segments, minSegmentLength=1,
            potentialBreaks=None, maxFirstBreak=None, minLastBreak=None):
        """
        model.ssr # sum-of-squares error
        model.fit_breaks # breakpoint locations
        model.n_parameters # number of model parameters
        model.n_segments # number of line segments
        model.beta # model parameters
        model.slopes # slope of each line segment
        model.intercepts # y intercepts of each line segment
        """

        max_c = None
        max_cor_coef = 0
        numSegCount = n_segments

        if potentialBreaks is None:
            potentialBreaks = self.t[1:-1]

        if maxFirstBreak is None:
            maxFirstBreak = self.t[-2]

        if minLastBreak is None:
            minLastBreak = self.t[1]

        if numSegCount <= 1:
            c = np.concatenate((self.t[:1], self.t[-1:]), axis=0)
            self.fit_with_breaks(c)
            return

        # print(potentialBreaks)
        cs = combinations(potentialBreaks, numSegCount - 1)
        # find the breaks with max cor_coef
        for c in cs:
            if (c[0] > maxFirstBreak or c[-1] < minLastBreak):
                continue
            c = np.concatenate((self.t[:1], np.array(c), self.t[-1:]), axis=0)
            if minSegmentLength > 1:
                c0 = np.concatenate((c[:1], c[:-1]), axis=0)
                c_diff = np.subtract(c, c0)
                if np.amin(c_diff[1:]) < minSegmentLength:
                    continue

            # print("fitting with:", c)
            self.fit_with_breaks(c)

            yp = self.predict()
            cor_ceofs = np.corrcoef(yp, self.y)

            if abs(cor_ceofs[0, 1]) > max_cor_coef:
                max_cor_coef = abs(cor_ceofs[0, 1])
                max_c = c
        # fill self object
        self.fit_with_breaks(max_c)
        return max_c

    def fit_with_breaks(self, breaks):
        """
        model.ssr # sum-of-squares error
        model.fit_breaks # breakpoint locations
        model.n_parameters # number of model parameters
        model.n_segments # number of line segments
        model.beta # model parameters
        model.slopes # slope of each line segment
        model.intercepts # y intercepts of each line segment
        """
        # M = len(c) + 1
        N = len(self.y)

        self.X = self.setupVirtualX(self.t, breaks)
        self.Y = self.y.reshape((N, 1))

        self.lm.fit(self.X, self.Y)
        self.beta = self.lm.coef_.flatten()
        self.fit_breaks = breaks
        self.n_parameters = len(self.beta)
        self.n_segments = self.n_parameters - 1

        return

    # T[0, 1, ..., N-1, N]
    # C[0, 1, ..., M-1, M]
    def setupVirtualX(self, T, C):
        # N = len(t)
        M = len(C)
        TT = T.reshape((-1, 1))

        def vFunc(vArr):
            t = vArr[0]
            x = np.zeros(M)
            x[0] = 1

            for j in range(1, M):
                # test where is t located [ *, C[j-1], *, C[j], *]
                if t > C[j]:
                    x[j] = C[j] - C[j-1]
                elif t < C[j - 1]:
                    break
                else:  # C[j-1] <= t <= C[j]
                    x[j] = t - C[j-1]
            return x

        X = np.apply_along_axis(vFunc, 1, TT)
        # print(C, X)

        return X[:, 1:]

    def predict(self, x=None):
        if x is None:
            yp = self.lm.predict(self.X).flatten()
        else:
            X = self.setupVirtualX(x, self.fit_breaks)
            yp = self.lm.predict(X).flatten()

        return yp


if __name__ == "__main__":
    input_filepath = "/Users/hurricane/share/data.txt"
    import pandas as pd
    df = pd.read_csv(input_filepath, sep='\t')

    nrow, ncol = df.shape
    da = df.to_numpy()

    x = da[:, 0]
    y = da[:, 1]
    xName = df.columns[0]
    yName = df.columns[1]
    yNamePred = df.columns[1] + "_PRED"

    # initialize piecewise linear fit with your x and y data
    model = PieceWiseLinearFitModel(x, y)
    model.fit(4, minSegmentLength=3)
    # fitfast(self, n_segments, pop=2, bounds=None, \*\*kwargs)

    print(model.fit_breaks)
    print(model.beta)

    # predict for the determined points
    yp = model.predict()
    print("y:", y)
    print("yp:", yp)

    # xHat = np.linspace(min(x), max(x), num=1000)
    # yHat = model.predict(xHat)
    # print("yHat:", yHat)
