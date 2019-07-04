# -*- coding: utf-8 -*-
import math
# from datetime import timedelta, datetime
from itertools import combinations

import numpy as np
import pandas as pd
from sklearn import linear_model

# index: [0,M]
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
    def __init__(self, y, t, pc):
        self.y = y
        self.t = t
        self.pc = pc

    def findSections(self):
        epsilon = 0.1
        threshold = 0.99
        N = len(self.t)
        r = [0] * (N + 1)

        r[0] = - math.inf
        t1 = datetime.now()
        for M in range(1, 6): # M segments, c[1, ..., M-1]
            r[M], c = self.MaxCorrcoef(M)
            t2 = datetime.now()
            print("-----------------------------------------")
            print("for {0} pieces, time comsuming {1} secends:".format(M, (t2-t1).seconds))
            print("max corrcoef {0} and breaks at {1}:".format(r[M], c))
            t2 = t1
            # need more conditions to stop iterator, for example: corrceoef is close to 1
            if r[M] > threshold: # or (r[M] - r[M -1]) < epsilon:
                print("M piecewise:", M, "\n")
                print("split points:", c, "\n")
                break

    def MaxCorrcoef(self, M):
        if M == 1:
            return self.calculateCorrceof(np.array([])), []

        # cs = combinations(self.t[1:-1], M - 1)
        cs = combinations(self.pc, M - 1)
        print(cs)
        max_c = None
        max_coef = -1
        for c in cs:
            # print(c)
            coef = self.calculateCorrceof(c)
            if coef > max_coef:
                max_coef = coef
                max_c = c
                print(c, coef, max_coef)

        return max_coef, max_c

    def calculateCorrceof(self, c):
        M = len(c) + 1
        N = len(y)

        if M == 1:
            X = self.t.reshape((N, 1))
            Y = self.y.reshape((N, 1))
            
        else:
            x_data = np.empty(shape=(N,M))
            X = D2Object(x_data)
            # C = D1Object(np.concatenate( (self.t[0:1], c, self.t[-1:])))
           
            cc = np.concatenate((np.array(c), self.t[-1:]), axis=0)
            # print(cc)
            C = D1Object( cc )
    
            for i in range(1, N+1):
                for j in range(1, M+1):
                    self.setVirtualXInteral(X, C, i, j)
    
            # tt = self.t.reshape((N,1))
            yy = self.y.reshape((N, 1))
            data = np.concatenate((x_data, yy), axis=1)
            x_names = ["M"+str(i) for i in range(1,M+1)]
            y_names = ["Y"]
            columns_hander = x_names + y_names
            df = pd.DataFrame(data,columns=columns_hander)
    
            X = df[x_names]
            Y = df[y_names]
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
                v = j
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
       
# -------- for test --------------------
#data = datasets.load_boston()
#medv = pd.DataFrame(data.target, columns=['MEDV'])
## medv.plot()
#y = medv.values
#t = np.arange(1, len(y) +1)
#
## print(y, t)
#pw = PieceWise(y, t)
#pw.findSections()
# ----------------------------

# paramters that affact the result
#
# the sie of figure, unit: inch
figsize=(12,8)
# rolling window size for smoothing, unit: day
avg_window = 31
# num of potential segment points 
num_potential_points = 20
# ----------------------------
# explore ndvi data and find potential segment points 
df = pd.read_csv("/Users/jiangzhu/workspace/igsnrr/data/ndvi/ndvi_2004.txt", sep='\t')
#df = pd.read_csv("/Users/jiangzhu/workspace/igsnrr/data/ndvi/ndvi_2004.txt", sep='\t', index_col=1)
(cn_row, cn_col) = df.shape
print(df.index)

df['NDVI_5AVG'] = df['NDVI_2004'].rolling(window=5, center=True).mean()
df['NDVI_11AVG'] = df['NDVI_2004'].rolling(window=11, center=True).mean()
df['NDVI_AVG'] = df['NDVI_2004'].rolling(window=avg_window, center=True).mean()

#df.plot(x='date', y=['NDVI_2004','EVI_2004','NDVI_5AV','NDVI_11AV','NDVI_15AV'], figsize=figsize)
# ndvi_df.plot(x='date', y='EVI_2004')

ndvi_avg = df['NDVI_AVG'].to_numpy()
ndvi_avg_grd1 = np.abs(np.gradient(ndvi_avg)) * 20
ndvi_avg_grd2 = np.gradient(ndvi_avg,2) * 40
ndvi_avg_grd3 = np.abs(np.gradient(np.gradient(ndvi_avg))) * 800
df['NDVI_GRD1'] = ndvi_avg_grd1
df['NDVI_GRD2'] = ndvi_avg_grd2
df['NDVI_GRD3'] = ndvi_avg_grd3
#df.plot(x='date', y=['NDVI_2004','EVI_2004','NDVI_5AV','NDVI_11AV','NDVI_15AV','NDVI_GRD1','NDVI_GRD2', 'NDVI_GRD3'], figsize=figsize)
nlargest_row = df.nlargest(num_potential_points,'NDVI_GRD3')
df['NLG_GRD'] = nlargest_row['NDVI_AVG']
nlargest_day = np.sort(nlargest_row['DOY'].to_numpy())
print("---------------")
print("potential points",nlargest_day)
# print(df['NLG_GRD'])

# plt.figure()
df.plot(x='DOY', y=['NDVI_2004','NDVI_AVG','NDVI_GRD1', 'NDVI_GRD3','NLG_GRD'],figsize= figsize)
# df.plot.scatter(x='DOY', y='NLG_GRD',figsize= figsize)

# 
t = df['DOY'].to_numpy()
y = df['NDVI_2004'].to_numpy()

# print(y, t, nlargest_day)
pw = PieceWise(y, t, nlargest_day)
pw.findSections()
