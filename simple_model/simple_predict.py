'''This module runs trained model on unseen data to produce predictions'''

import pandas as pd
import cPickle as pickle
import statsmodels.api as sm
import matplotlib.pyplot as plt
from datetime import timedelta

class PredictARMA(object):
    """docstring for ."""
    def __init__(self, path_to_model):
        self.path_to_model = path_to_model
        self.model_unpickled = None
        with open(self.path_to_model) as f_un:
            print
            print '## Loading Model'
            print
            self.model_unpickled = pickle.load(f_un)
        #
        self.start_day = None
        self.end_day = None

    def predict(self, df):
        start_day = df.index[0].date() - timedelta(days=1)
        end_day = start_day + timedelta(days=2)
        self.start_day = str(start_day)
        self.end_day = str(end_day)
        print 'start_day: ', start_day
        print 'end_day: ', end_day
        print
        pred = self.model_unpickled.predict(start=self.start_day, end=self.end_day)
        return pred

    def plot_pred_timeseries(self, df, pred):
        # INPUT: DataFrame, Series
        date_from = pd.to_datetime(self.start_day).date()
        date_to = pd.to_datetime(self.end_day).date()
        df_data = df.query('index >= @date_from and index <= @date_to')
        #
        plt.figure(figsize=(18,5))
        # plotting data
        x = df_data.index
        y = df_data[df_data.columns[0]].values
        plt.plot(x, y, color='b')
        #
        #plotting prediction
        xpred = pred.index
        ypred = pred.values
        plt.plot(xpred, ypred, color='g')
        #
        plt.xlabel('time')
        plt.ylabel(df_data.columns[0])
        #plt.title('Data for the following household: {}'.format(name))
        plt.show()
