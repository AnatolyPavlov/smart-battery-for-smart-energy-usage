'''This module runs trained model on unseen data to produce predictions'''

import pandas as pd
import cPickle as pickle
import statsmodels.api as sm
import matplotlib.pyplot as plt
from datetime import timedelta
pd.options.mode.chained_assignment = None

# Custom Modules:
from auxiliary_functions import print_process

class PredictARMA(object):
    """docstring for ."""
    def __init__(self, household_id, model_name):
        self.household_id = household_id
        self.model_name = model_name
        self.model_unpickled = None
        path_to_model = '../saved_models/'+self.household_id+'_'+self.model_name+'.pkl'
        with open(path_to_model) as f_un:
            print_process('Loading Model')
            self.model_unpickled = pickle.load(f_un)
        #
        self.start_day = None
        self.end_day = None

    def predict(self, df):
        start_day = df.index[0].date() - timedelta(days=1)
        end_day = start_day + timedelta(days=2)
        self.start_day = str(start_day)
        self.end_day = str(end_day)
        print_process('Making predictions for the time span specified below:')
        print 'start_day: {}'.format(self.start_day)
        print 'end_day: {}'.format(self.end_day)
        print
        pred = self.model_unpickled.predict(start=self.start_day, end=self.end_day)
        print_process('Saving Predictions:')
        s = pd.Series(pred.values, index=pred.index)
        s = pd.DataFrame(s.values, columns=[df.columns[0]], index=s.index)
        path_to_pred = \
        '../predictions/'+self.household_id+'_'+self.model_name+'_'+self.start_day+'_'+self.end_day+'.csv'
        s.to_csv(path_to_pred)
        print 'Predictions saved into: {}'.format(path_to_pred)
        print
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
