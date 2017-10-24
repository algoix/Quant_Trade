import zmq
import datetime
import pandas as pd
import numpy as np
import numpy
from numpy import inf

import json
import plotly_stream as plyst
import plotly.tools as plyt
import plotly.plotly as ply
#!pip install plotly
import tpqib
import datetime

#from sklearn.cross_validation import train_test_split
from sklearn import linear_model
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

import matplotlib.pyplot as plt

import pickle

     
# saving linear model

data=data.dropna()
data=data.tail(1000)
X=data[['close','price','P','vel','sigma','U','D','BA']]
y=data[['ret']]
regr = linear_model.LinearRegression()
regr_model=regr.fit(X,y)
regr_model = pickle.dumps(regr_model)
# Fit regression model
svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.9) #kernel='linear' #kernel='poly'
svr_model = svr_rbf.fit(X, y)
svr_model = pickle.dumps(svr_model)

# saving classification model

X=data[['close','price','P','ret','vel','sigma','BA']]
y1=data[['U']]
y2=data[['D']]
pr_df=X.tail(360)
svm = SVC(kernel='linear')
lm = linear_model.LogisticRegression(C=1e4)
svm_model_up= svm.fit(X.tail(1000),y1.tail(1000))
svm_model_up = pickle.dumps(svm_model_up)
lm_model_up= lm.fit(X.tail(1000), y1.tail(1000))
lm_model_up = pickle.dumps(lm_model_up)
svm_model_dn= svm.fit(X.tail(1000), y2.tail(1000))
svm_model_dn = pickle.dumps(svm_model_dn)
lm_model_dn= lm.fit(X.tail(1000), y2.tail(1000))
lm_model_dn = pickle.dumps(lm_model_dn)

#loading regression model, first save the model
svr_model = pickle.loads(svr_model)
regr_model = pickle.loads(regr_model)

#loading classification model, first save the model

svm_model_up = pickle.loads(svm_model_up)
svm_model_dn = pickle.loads(svm_model_dn)
lm_model_up = pickle.loads(lm_model_up)
lm_model_dn = pickle.loads(lm_model_dn)

def strat_lr(data):
    #data=preprocessing_df(data)
    data=data.dropna()
    data=data.tail(1000)
    X=data[['close','price','P','vel','sigma','U','D','BA']]
    y=data[['ret']]
    predict_regr=regr_model.predict(X)
    predict_svr=svr_model.predict(X)
    dt=data[['price']]
    dt['predict_regr']=predict_regr
    dt['predict_regr']=dt.price+dt.price*dt.predict_regr
    dt['predict_svr']=predict_svr
    dt['predict_svr']=dt.price+dt.price*dt.predict_svr
    
    pdf=data
    pdf['pREG']=dt.predict_regr
    pdf['pSVR']=dt.predict_svr
         
    #dt=data[['price','predict']]
    return pdf
def classification_up_dn(data):
    X=data[['close','price','P','ret','vel','sigma','BA']]
    y1=data[['U']]
    y2=data[['D']]
    pr_df=X.tail(360)
    predict_svm_up=svm_model_up.predict(X.tail(360))
    pr_df['predict_svm_up']=predict_svm_up
    predict_lm_up=lm_model_up.predict(X.tail(360))
    pr_df['predict_lm_up']=predict_lm_up
    predict_svm_dn=svm_model_dn.predict(X.tail(360))
    pr_df['predict_svm_dn']=predict_svm_dn
    predict_lm_dn=lm_model_dn.predict(X.tail(360))
    pr_df['predict_lm_dn']=predict_lm_dn
    pr_df['predict_svm']=pr_df.predict_svm_up+pr_df.predict_svm_dn
    pr_df['predict_lm']=pr_df.predict_lm_up+pr_df.predict_lm_dn
    return pr_df

def data_list(data):
    close_list=[]
    price_list=[]
    ret_list=[]
    vel_list=[]
    spread_list=[]
    sigma_list=[]
    vel_c_list=[]
    mom_list=[]
    UD_list=[]
    P_list=[]
    UT_list=[]
    DT_list=[]
    BA_list=[]
    close_list=data.close.tolist()
    price_list=data.price.tolist()
    return close_list,price_list
    

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

from keras.models import load_model
model = load_model('elevenaug.h5')

# convert an array of values into a dataset matrix for LSTM
def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back), 0]
        b = dataset[i:(i+look_back), 1]
        c = dataset[i:(i+look_back), 2]
        d = dataset[i:(i+look_back), 3]
        e=  dataset[i:(i+look_back), 4]
        f=  dataset[i:(i+look_back), 5]
        g=  dataset[i:(i+look_back), 6]
        dataX.append(numpy.c_[a,b,c,d,e,f,g])
        #dataX.append(b)
        #dataX.append(c)
        #dataX.append(d)
        #dataX.append(e)
        #dataX.concatenate((a,bT,cT,dT,eT),axis=1)
        dataY.append(dataset[i + look_back, 0])
    return numpy.array(dataX), numpy.array(dataY)

def strat_LSTM(data):
    #data=preprocessing_df(df)
    #pr=strat_class(data)
    data=data[['close','vel','sigma','P','pREG','predict_svm','predict_lm']]  
    dataset = data.values
    dataset = dataset.astype('float32')

    # normalize the dataset
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)
    # reshape into X=t and Y=t+1
    look_back = 3
    dataX, dataY = create_dataset(dataset,look_back)
    # reshape input to be [samples, time steps, features]
    dataX = numpy.reshape(dataX, (dataX.shape[0],dataX.shape[1],dataX.shape[2]))
    # make predictions
    Predict = model.predict(dataX)
    #plt.plot(dataY)
    #plt.plot(Predict)
    #plt.show()
    #return Predict
    return numpy.array(Predict), numpy.array(dataY)

# Import a Kalman filter and other useful libraries
from pykalman import KalmanFilter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import poly1d

def kalman_ma(data):
    x=data.price.tail(1000)
    y=data.close.tail(1000)
    # Construct a Kalman filter
    kf = KalmanFilter(transition_matrices = [1],
                  observation_matrices = [1],
                  initial_state_mean = 0,
                  initial_state_covariance = 1,
                  observation_covariance=1,
                  transition_covariance=.01)

    # Use the observed values of the price to get a rolling mean
    state_means, _ = kf.filter(x.values)
    state_means = pd.Series(state_means.flatten(), index=x.index)
    return state_means