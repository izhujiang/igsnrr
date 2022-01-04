from itertools import combinations
import numpy as np

# from sklearn import linear_model
import statsmodels.api as sm

import scipy.stats as stats
import matplotlib.pyplot as plt


vertualxCache = {}
def setupVirtualX(T, C):
        """
        T: t serials, np.array
        C: breaks, include both ends, np.array
        """
        key = C.tobytes()
        if key in vertualxCache:
            return vertualxCache[key]

        N = T.size
        M = C.size
        X = np.zeros((N, M))

        # print(C)
        deltaC = np.diff(C)
        
        # X = np.piecewise(TT, [TT > CC, TT>=CC0 and TT<CC], [deltaCC, TT-CC0])
        for j in range(1, M):
            # # test where is t located [ *, C[j-1], *, C[j], *]
            # if T > C[j]:
            idx =T > C[j], j
            X[idx] = deltaC[j - 1] # C[j] - C[j-1]
            # elif T < C[j - 1]:
                # break
            # else:  # C[j-1] <= t <= C[j]
            idx = np.logical_and(C[j-1] <= T, T<= C[j])
            X[idx, j] = T[idx] - C[j-1]
        
        # [1, x1, x2, x3...] for X * B = Y
        X[:, :1] = 1

        vertualxCache[key] = X
        return X
        # return X[:,1:]


class PieceWiseLinearFitModel:
    def __init__(
            self,
            t, y, n_maxSegments, minSegmentLength=1,
            potentialBreaks=None, maxFirstBreak=None, minLastBreak=None):
        """
        t, y with shape of (N, 1)
        t, y, np.array
        """
        self.t = t

        self.y = y
        # self.Y = self.y.reshape((-1, 1))

        # self.lm = linear_model.LinearRegression(fit_intercept=True, copy_X=True)
        # self.lm = linear_model.LinearRegression(copy_X=True)
        self.setupPotentialBreaks(n_maxSegments, minSegmentLength, potentialBreaks, maxFirstBreak, minLastBreak)

    def findMaxScoreBreaksAtNSegments(self, n_segments):
        """
        max_r_sq, max coef at level of n segments
        max_c, 

        """
        max_r_sq_breaks = None
        max_rsqrd = 0

        # find the breaks with max cor_coef
        cs = self.cs_arr[n_segments - 1]
        max_r_sq = 0
        # print("n_segments and breaks list:", n_segments, cs)
        for c in cs:
            # print("fitting with:", c)

            X = setupVirtualX(self.t, c)
            # print(X[:5])
            # print(y[:5])

            model = sm.OLS(self.y, X)
            results = model.fit()
            r_sq = results.rsquared
            if r_sq > max_r_sq: 
                max_r_sq = r_sq
                max_r_sq_breaks = c

        # fill self object
        # print("n_segments:", n_segments, "max_r_sq:", max_r_sq, "max_cor:", math.sqrt(max_r_sq), "max_r_sq_breaks", max_r_sq_breaks)
        # self.fit_with_breaks(max_c)
        return max_r_sq, max_r_sq_breaks
    
    def fit(self, breaks):
        """
        model.fit_breaks # breakpoint locations, type: np.array
        """
        # self.X = self.setupVirtualX(self.t, breaks)
        self.X = setupVirtualX(self.t, breaks)

        # print("X:", self.X, "y:", self.y)
        model = sm.OLS(self.y, self.X)
        results = model.fit()

        self.beta = results.params
        self.fit_breaks = breaks
        self.n_parameters = self.beta.size
        self.n_segments = breaks.size - 1

        return results

    # def setupVirtualX(self, T, C):
    #     """
    #     T: t serials, np.array
    #     C: breaks, include both ends, np.array
    #     """

    #     N = T.size
    #     M = C.size
    #     X = np.zeros((N, M))

    #     # print(C)
    #     deltaC = np.diff(C)
        
    #     # X = np.piecewise(TT, [TT > CC, TT>=CC0 and TT<CC], [deltaCC, TT-CC0])
    #     for j in range(1, M):
    #         # # test where is t located [ *, C[j-1], *, C[j], *]
    #         # if T > C[j]:
    #         idx =T > C[j], j
    #         X[idx] = deltaC[j - 1] # C[j] - C[j-1]
    #         # elif T < C[j - 1]:
    #             # break
    #         # else:  # C[j-1] <= t <= C[j]
    #         idx = np.logical_and(C[j-1] <= T, T<= C[j])
    #         X[idx, j] = T[idx] - C[j-1]
        
    #     # [1, x1, x2, x3...] for X * B = Y
    #     X[:, :1] = 1
    #     return X
    #     # return X[:,1:]

    def evaluateModelPerformce(self, breaks):
        reg  = self.fit(breaks)
        yp = reg.predict(self.X)

        g_r_value, g_p_value = stats.pearsonr(self.y, yp)

        # calclate Corrceof piece by piece
        M = len(breaks) - 1
        r_values = [0] * M
        p_values = [0] * M

        p0 = self.t[0]
        for i in range(0, M):
            p1 = breaks[i+1]
            indexs = np.logical_and(self.t >= p0, self.t <= p1)
            if len(self.t[indexs]) < 2:
                print(breaks)
                print("skipping p0-p1:", p0, p1)
                continue
            # print("p0-p1:",p0, p1)
            # print("x:", x[indexs])
            # print("y:", y[indexs])
            r_values[i], p_values[i] = stats.pearsonr(yp[indexs], self.y[indexs])
            p0 = p1

        # return rs, p_values
        pwRes = PieceWiseLinearResult(
            generalCorcoef = g_r_value,
            generalPvalue = g_p_value,
            breaks = breaks,
            regcoefs = self.beta,
            psCorcoefs = r_values,
            psPvalues = p_values,
            yPred = yp)
        return pwRes


    def setupPotentialBreaks(self, n_maxSegments, minSegmentLength=1,
            potentialBreaks=None, maxFirstBreak=None, minLastBreak=None):
        """
        n_segments # number of line segments
        minSegmentLength # minimin length of every single segment
        potentialBreaks  # potential vilid breaks, None for all breaks
        maxFirstBreak    # the first valid break
        minLastBreak     # the last valid break
        """
        self.n_maxSegments = n_maxSegments
        self.minSegmentLength = minSegmentLength

        if potentialBreaks is None:
            self.potentialBreaks = self.t[1:-1]

        if maxFirstBreak is None:
            self.maxFirstBreak = self.t[-2]

        if minLastBreak is None:
            self.minLastBreak = self.t[1]

        self.cs_arr = [np.empty(1, dtype=int)]* self.n_maxSegments
        self.cs_arr[0] =np.array([np.concatenate((self.t[:1], self.t[-1:])) ])

        def isValidBreaksRange(brk):
            if (brk[0] > self.maxFirstBreak or brk[-1] < self.minLastBreak):
                return True
            else:
                return False

        breaks = self.potentialBreaks # not include both ends
        for k in range(1, self.n_maxSegments):
            if not (maxFirstBreak is None and minLastBreak is None):
                validBreaks = filter(isValidBreaksRange, combinations(breaks, k))
                self.cs_arr[k] = np.array([ np.concatenate((self.t[:1], np.asarray(a), self.t[-1:])) for a in validBreaks])
            else:
                self.cs_arr[k] = np.array([ np.concatenate((self.t[:1], np.asarray(a), self.t[-1:])) for a in combinations(breaks, k)])

            # filter out invlide breaks whose length less than minsegmentLength
            delta = np.diff(self.cs_arr[k])
            min_delta = np.amin(delta, axis=1)
            # print(min_delta)
            # print("before filter:", self.cs_arr[k].size,  self.cs_arr[k])
            self.cs_arr[k] = self.cs_arr[k][min_delta >= self.minSegmentLength]
            # print("after filter:", self.cs_arr[k].size, self.cs_arr[k])

class PieceWiseLinearRegressionContext:
    def __init__(
            self,
            minSegmentCount=1,
            maxSegmentCount=4,
            minSegmentLength=1,
            ceofDiffEpsilon=0.00001,
            ceofThreshold=0.99,
            debugLevel=0, **kwargs):

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
            generalCorcoef,
            generalPvalue,
            breaks,
            regcoefs,
            psCorcoefs,
            psPvalues,
            yPred):
        self.generalCorcoef = generalCorcoef
        self.generalPvalue = generalPvalue
        self.breaks = breaks
        self.regcoefs = regcoefs
        self.psCorcoefs = psCorcoefs
        self.psPvalues = psPvalues
        self.yPred = yPred

def DoPieceWise(t, y, ctx):
    model = PieceWiseLinearFitModel(t, y, n_maxSegments=ctx.maxSegmentCount, minSegmentLength= ctx.minSegmentLength)

    minSeg = ctx.minSegmentCount
    maxSeg = ctx.maxSegmentCount

    m_max_r_sq = 0
    m1_max_r_sq = 0
    m_max_r_sq_breaks = np.concatenate((t[:1], t[-1:]))
    m1_max_r_sq_breaks = m_max_r_sq_breaks 

    for M in range(minSeg, maxSeg + 1):
        m_max_r_sq, m_max_r_sq_breaks = model.findMaxScoreBreaksAtNSegments(M)
        # fitfast(self, n_segments, pop=2, bounds=None, \*\*kwargs)

        # stop iterating by conditions:
        # 1. when max corrcoef is close to 1 (over threshold)
        sc = M
        if abs(m_max_r_sq) > ctx.threshold:
            break
        # 2. when corrcoef varies small enough
        if abs(m_max_r_sq - m1_max_r_sq) < ctx.epsilon:
            m_max_r_sq = m1_max_r_sq
            m_max_r_sq_breaks = m1_max_r_sq_breaks
            break

        m1_max_r_sq = m_max_r_sq 
        m1_max_r_sq_breaks = m_max_r_sq_breaks 


    pwRes = model.evaluateModelPerformce(m_max_r_sq_breaks)
    return pwRes

# -----------------------------------------------------------------
# Tests

def initTestData():
    x = np.asarray([2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
                   2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021])
    y = np.asarray([276.84527587890625, 358.33203125, 314.0, 62.0, 100.0, 83.0, 415.0, 366.29766845703125,
                    454.0, 372.99871826171875, 137.8452606201172, 344.806884765625, 102.0, 284.2381286621094,
                    243.0, 512.0, 458.0, 349.8360290527344, 48.84526062011719, 140.0, 301.5119323730469, 327.0])

    return x,y

def testSetupBreaks():
    x, y = initTestData()

    model = PieceWiseLinearFitModel(x, y)
    model.setupPotentialBreaks(4, 3)
    # self.setupPotentialBreaks(n_maxSegments, minSegmentLength, potentialBreaks, maxFirstBreak, minLastBreak)
    C = np.array([2000, 2005, 2012, 2021])
    X = setupVirtualX(x, C)
    print(X)
 
def testFindMaxScoreBreaks():
    x,y = initTestData()
    model = PieceWiseLinearFitModel(x, y, n_maxSegments=4, minSegmentLength=3)
    model.findMaxScoreBreaksAtNSegments(4)
    
def testFit():
    C = np.array([2000.0, 2005.0, 2012.0, 2021.0])
    x,y = initTestData()
    model = PieceWiseLinearFitModel(x, y, n_maxSegments=4, minSegmentLength=3)
    model.fit(C)

def testDoPieceWise():
    x,y = initTestData()
    ctx = PieceWiseLinearRegressionContext(
            recordNumber=22,
            minSegmentCount=1,
            maxSegmentCount=4,
            minSegmentLength=3,
            ceofThreshold=0.90,
            ceofDiffEpsilon=0.000001,
            debugLevel=0,
        )
    pwRes = DoPieceWise(x, y, ctx)
    print("generalCorcoef:", pwRes.generalCorcoef)
    print("generalPvalue:", pwRes.generalPvalue)
    print("breaks:", pwRes.breaks)
    print("psCorcoefs:", pwRes.psCorcoefs)
    print("psPvalues:", pwRes.psPvalues)
    plt.plot(x, y, 'o')
    plt.plot(x, pwRes.yPred, '-')
    print(pwRes)


def setupVirtualXPerformceProfile():
    x, y = initTestData()

    model = PieceWiseLinearFitModel(x, y)
    C = np.array([2000, 2005, 2012, 2021])
    X = setupVirtualX(x, C)
    print(X)

def fitWithBreaksPerformceProfile():
    C = np.array([2000.0, 2005.0, 2012.0, 2021.0])
    x,y = initTestData()
    potentialBreaks = x[1:-1]
    for i in range(50):
        y  =  y + np.random.randint(5, size=(22))
        model = PieceWiseLinearFitModel(x, y)

        # cs = combinations(potentialBreaks, 3)
        # for c in cs:
        for k in range(1140):
            # c = np.concatenate((x[:1], np.array(c), x[-1:]), axis=0)
            model.fit_with_breaks(C)

            # yp = model.predict()
            # cor_ceofs = np.corrcoef(yp, y)

    # print(datetime.datetime.now())

def wholeFitPerformceProfile():
    C = np.array([2000.0, 2005.0, 2012.0, 2021.0])

    x,y = initTestData()
    for i in range(50):
        y  =  y + np.random.randint(5, size=(22))
        model = PieceWiseLinearFitModel(x, y, n_maxSegments=4, minSegmentLength=3)
        model.fit(C)

    # print(datetime.datetime.now())

def DoPiecewiseProfile():
    x,y = initTestData()
    ctx = PieceWiseLinearRegressionContext(
            minSegmentCount=1,
            maxSegmentCount=4,
            minSegmentLength=3,
            ceofThreshold=0.90,
            ceofDiffEpsilon=0.000001,
            debugLevel=0,
        )

    for i in range(500):
        y  =  y + np.random.randint(5, size=(22))
        pwRes = DoPieceWise(x, y, ctx)

def testSuit():
    # testSetupBreaks()
    # testFitWithBreaks()
    # testFit()
    testDoPieceWise()

# performce profiling 
# 1. Whole program profiling
# python -m cProfile -s cumtime pwlfm.py > log
# 
# 2. Targeted profiling( using cProfile script as following):
# https://www.toucantoco.com/en/tech-blog/python-performance-optimization
# 3. Line profiling
# https://github.com/rkern/line_profiler
def perfromceSuit():
    # import cProfile
    # cp = cProfile.Profile()
    # cp.enable()

    # fitWithBreaksPerformceProfile()
    # wholeFitPerformceProfile()
    DoPiecewiseProfile()

    # cp.disable()
    # cp.print_stats()

if __name__ == "__main__":
    # testSuit()
    perfromceSuit()