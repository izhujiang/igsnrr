# -*- coding: utf-8 -*-
import math
# from datetime import timedelta, datetime
from itertools import combinations
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn import linear_model
import matplotlib.pyplot as plt


# index: [1,M]
class D1Object:
    # c: numpy.array
    def __init__(self, c):
        self.c = c

    def valueAt(self, k):
        return self.c[k-1]

    def toString(self):
        return ','.join(str(x) for x in self.c) # '0,3,5'


# index: [1, 1] - [N, M]
class D2Object:
    # x: 2-D numpy.array
    def __init__(self, x):
        self.x = x

    def valueAt(self, i, j):
        return self.x[i - 1, j -1]

    def setValueAt(self, i, j, v):
        self.x[i - 1, j -1] = v

class PieceWise:
    def __init__(self, y, t, pc, debug=False):
        self.y = y
        self.t = t
        self.pc = pc
        self._debug = debug

    def findSections(self):
        epsilon = CEOF_DIFF_EPSILON 
        threshold = CEOF_THRESHOLD
        N = len(self.t)
        
        M = (len(self.pc) + 1)
        r = [0] * M
        c = [[]]* M
        MAX_SEGMENTS_COUNT = M

        r[0] = - math.inf
        t1 = datetime.now()
        for M in range(1, MAX_SEGMENTS_COUNT): # M segments, c[1, ..., M-1]
            r[M], c[M] = self.MaxCorrcoef(M)
            if self._debug:
                t2 = datetime.now()
                print("-----------------------------------------")
                print("for {0} pieces, time comsuming {1} secends:".format(M, (t2-t1).seconds))
                print("max corrcoef {0} and breaks at {1}:".format(r[M], c[M]))
                t2 = t1
            
            # stop iterator by following condition
            if r[M] > threshold:  # when max corrcoef is close to 1 (over threshold)
                print("{0} piecewise  and split points:{1} with max corrcoef {2}. \n".format(M, c[M], r[M]))
                return r[M], c[M]
            if (r[M] - r[M -1]) < epsilon:# when corrcoef varies small enough during the iterate 
                print("{0} piecewise  and split points:{1} with max corrcoef {2}. \n".format(M-1, c[M-1], r[M-1]))
                return r[M-1], c[M-1]
        

    def MaxCorrcoef(self, M):
        if M == 1:
            return self.calculateCorrceof([]), []

        # cs = combinations(self.t[1:-1], M - 1)
        cs = combinations(self.pc, M - 1)
        if self._debug:
            print(cs)
            
        max_c = None
        max_coef = -1
        for c in cs:
            # print(c)
            coef = self.calculateCorrceof(c)
            if coef > max_coef:
                max_coef = coef
                max_c = c
                if self._debug:
                    print(c, coef, max_coef)

        return max_coef, max_c

    def calculateCorrceof(self, c):
        M = len(c) + 1
        N = len(self.y)

        if M == 1:
            X = self.t.reshape((N, 1))
            Y = self.y.reshape((N, 1))

        else:
            x_data = np.empty(shape=(N,M))
            XX = D2Object(x_data)
            # C = D1Object(np.concatenate( (self.t[0:1], c, self.t[-1:])))

            cc = np.concatenate((np.array(c), self.t[-1:]), axis=0)
            # print(cc)
            CC = D1Object( cc )

            for i in range(1, N+1):
                for j in range(1, M+1):
                    self.setVirtualXInteral(XX, CC, i, j)

            # tt = self.t.reshape((N,1))
            yy = self.y.reshape((N, 1))
            # data = np.concatenate((x_data, yy), axis=1)
#            x_names = ["M"+str(i) for i in range(1,M+1)]
#            y_names = ["Y"]
#            columns_hander = x_names + y_names
#            df = pd.DataFrame(data,columns=columns_hander)

#            X = df[x_names]
#            Y = df[y_names]
            Y = yy
            X = x_data
            # print(df)

        # print(X, Y)
        # with sklearn
        lm = linear_model.LinearRegression()
        lm.fit(X, Y)
        # predictions = lm.predict(x_data)

        score = lm.score(X,Y)
        # plt.scatter(y, predictions)
        # print("the coefficients:\n", lm.coef_)
        # print("the estimated intercepts:\n", lm.intercept_)
        # print("Score:\n", lm.intercept_)

        return score
        # return regr

    # c[1, ..., M-1]
    def setVirtualXInteral(self, X, C, i, j):
        v = None
        # print(C.toString(), '[', i, j, ']')
        if j == 1:
            if(i <=C.valueAt(1)):
                v = i
            else:
                v = C.valueAt(1)
        else:
            if( i <= C.valueAt(j -1)):
                v = 0
            elif( i > C.valueAt(j)):
                v =  C.valueAt(j) - C.valueAt(j-1)
            else:
                v = i - C.valueAt(j - 1)

        X.setValueAt(i,j,v)

# -------- Helper functions --------------------
def doCalc(df):
    (cn_row, cn_col) = df.shape
    df['NDVI_5AVG'] = df['NDVI_2004'].rolling(window=5, center=True).mean()
    df['NDVI_11AVG'] = df['NDVI_2004'].rolling(window=11, center=True).mean()
    df['NDVI_AVG'] = df['NDVI_2004'].rolling(window=ROLLING_WINDOW_SIZE, center=True).mean()
    
    ndvi_avg = df['NDVI_AVG'].to_numpy()
    ndvi_avg_grd1 = np.abs(np.gradient(ndvi_avg)) * 20
    #ndvi_avg_grd2 = np.gradient(ndvi_avg,2) * 40
    
    ndvi_avg_grd2 = np.abs(np.gradient(np.gradient(ndvi_avg))) * 600
    df['NDVI_GRD1'] = ndvi_avg_grd1
    df['NDVI_GRD2'] = ndvi_avg_grd2
    #df.plot(x='date', y=['NDVI_2004','EVI_2004','NDVI_5AV','NDVI_11AV','NDVI_15AV','NDVI_GRD1','NDVI_GRD2', 'NDVI_GRD3'], figsize=figsize)
    nlargest_row = df.nlargest(NUM_POTENTIAL_SEGMENT_POINTS,'NDVI_GRD2')
    df['NLG_GRD'] = nlargest_row['NDVI_AVG']
    nlargest_day = np.sort(nlargest_row['DOY'].to_numpy())
    print("---------------")
    print("potential points",nlargest_day)
    # print(df['NLG_GRD'])
    
    t = df['DOY'].to_numpy()
    y = df['NDVI_2004'].to_numpy()
    
    # print(y, t, nlargest_day)
    # pw = PieceWise(y, t, nlargest_day)
    # setup debug=True in PieceWise constructor, if want to print debug info
    pw = PieceWise(y, t, nlargest_day, debug=True)
    max_coef, pc = pw.findSections()
    c = pc + (cn_row,)
    start = 0
    preds = np.empty((1, 0))
    for end in c:
        X = t[start: end].reshape(-1, 1)
        # Y = y[start: end].reshape(-1, 1)
        Y = y[start: end]
        # print(X, Y)
    
        lm = linear_model.LinearRegression()
        lm.fit(X, Y)
        
        # predictions = lm.predict(x_data)
        score = lm.score(X,Y)
        # print(score)
        predictions = lm.predict(X)
        #print(predictions)
        #df['NDVI_PRED'][start-1: end] = predictions
        # block = np.concatenate((X, Y, predictions), axis=1)
        #print(X)
        #print(Y)
        #print(block)
        preds = np.append(preds, predictions)
        start= end
        
    #preds_df = pd.DataFrame(preds,columns=['X', 'Y', 'NDVI_PRED'])
    # print(preds, preds.size)
    df['NDVI_PRED'] = preds
    
    
def display(df):
    # Plot outputs
    (cn_row, cn_col) = df.shape
    x = df['DOY']
    ndvi =df['NDVI_2004']
    nlg =df['NLG_GRD']
    
    ndvi_avg =df['NDVI_AVG']
    ndvi_avg_5 =df['NDVI_5AVG']
    ndvi_avg_11 =df['NDVI_11AVG']
    nlg =df['NLG_GRD']
    
    ndvi_grd1 = df['NDVI_GRD1']
    ndvi_grd2 = df['NDVI_GRD2']
    
    ndvi_pred = df['NDVI_PRED']
    
    
    plt.figure(figsize=FIG_SIZE)
    plt.xlim(left=0, right=cn_row) 
    plt.ylim(bottom=0, top=0.4) 
    
    plt.scatter(x, nlg,  color='black')
    annos = df[pd.notna(df['NLG_GRD'])][['DOY', 'NLG_GRD']]
    # print(annos)
    
    old_x = old_y = 1e9 # make an impossibly large initial offset
    thresh = 2 #make a distance threshold
    for row in annos.itertuples():
        px,py = row[1], row[2]
        label = "{}".format(px)
        
        #calculate distance
        d = ((px-old_x)**2+(py-old_y)**2)**(.5)
        #if distance less than thresh then flip the arrow
        flip = 1
        # print(d)
        if d < thresh: flip=-2
    
        plt.annotate(
            label,
            xy = (px, py), xytext = (-20*flip, 5*flip),
            textcoords = 'offset points', ha = 'right', va = 'bottom',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
        old_x = px
        old_y = py

    # plt.plot(x, ndvi, color='blue', linewidth=1)
    ndvi_line, = plt.plot(x, ndvi, label="NDVI", linewidth=1)
    ndvi_avg_line, = plt.plot(x, ndvi_avg, label="NDVI_AVG", linewidth=1)
    ndvi_avg_line5, = plt.plot(x, ndvi_avg_5, label="NDVI_AVG5", linewidth=1)
    ndvi_avg_line11, = plt.plot(x, ndvi_avg_11, label="NDVI_AVG11", linewidth=1)
    ndvi_grd1_line, = plt.plot(x, ndvi_grd1, label="NDVI_GRD1", linewidth=1)
    ndvi_grd2_line, = plt.plot(x, ndvi_grd2, label="NDVI_GRD2", linewidth=1)
    ndvi_pred_line, = plt.plot(x, ndvi_pred,color='blue', label="NDVI_PRED", linewidth=1)
    
    handles=[ndvi_line,
             ndvi_avg_line,
             ndvi_avg_line5,
             ndvi_avg_line11,
             ndvi_grd1_line,
             ndvi_grd2_line,
             ndvi_pred_line]
    
    plt.legend(handles = handles, loc='upper right')

    
    #df.plot(x='DOY', y=['NDVI_2004','NDVI_AVG','NDVI_5AVG', 'NDVI_11AVG','NDVI_GRD1', 'NDVI_GRD2','NLG_GRD', 'NDVI_PRED'],figsize= FIG_SIZE)
    #df.plot.scatter(x='DOY', y='NLG_GRD',figsize= FIG_SIZE)
    
    
# paramters that affact the result
#
# the sie of figure, unit: inch
FIG_SIZE=(16,12)
# rolling window size for smoothing, unit: day
ROLLING_WINDOW_SIZE = 31
# num of potential segment points 
NUM_POTENTIAL_SEGMENT_POINTS = 30

# threshold for stop calculating Corrceof
CEOF_THRESHOLD = 0.98
CEOF_DIFF_EPSILON = 0.001

# ----------------------------
# explore ndvi data and find potential segment points 
df = pd.read_csv("/Users/jiangzhu/workspace/igsnrr/data/ndvi/ndvi_2004.txt", sep='\t')
#df = pd.read_csv("/Users/jiangzhu/workspace/igsnrr/data/ndvi/ndvi_2004.txt", sep='\t', index_col=1)

doCalc(df)
display(df)