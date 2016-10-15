'''This module contains arma model. It takes post-processed data provided via
simple_main.py module, splits these data into training and validating subsets,
trains model on training data and validates on validation data set. It saves
trained model as .pkl file, so that it can be uploaded and used to make predictions
and/or test the model on test data set.'''

import pandas as pd
import statsmodels.api as sm
import cPickle as pickle
import matplotlib.pyplot as plt

# Custom Modules:
from auxiliary_functions import print_process

class TimeSeriesDataSplit(object):

    def __init__(self, household_id, train_days):
        self.train_days = train_days
        self.household_id = household_id

    def train_test_split(self, df):
        if self.train_days < 1:
            print 'There must be at least one day in training set!'
            return
        days = []
        for i, datetime in enumerate(df.index):
            if datetime.date() not in days:
                days.append(datetime.date())
        print '{}th day: {}'.format(self.train_days, days[self.train_days-1])
        self.test_set_first_date = days[self.train_days]
        #
        df_train = df.query('index < @self.test_set_first_date')
        df_test = df.query('index >= @self.test_set_first_date')
        print
        print 'Training data set'
        print df_train.head()
        print df_train.tail()
        print
        print 'Test data set'
        print df_test.head()
        print df_test.tail()
        print_process('Saving Train and Test Data')
        path_to_train_data = '../clean_data/'+self.household_id+'_train.csv'
        path_to_test_data = '../clean_data/'+self.household_id+'_test.csv'
        df_train.to_csv(path_to_train_data)
        df_test.to_csv(path_to_test_data)
        print 'Train data saved into: {}'.format(path_to_train_data)
        print 'Test data saved into: {}'.format(path_to_test_data)
        return df_train, df_test

class ModelARMA(object):

    def __init__(self, household_id, p, q, trend, freq=None):
        self.household_id = household_id
        self.p = p
        self.q = q
        self.trend = trend
        self.freq = freq

    def fit(self, df_train):
        model = sm.tsa.ARMA(df_train, order=(self.p, self.q), freq=self.freq)
        model_res = model.fit(trend=self.trend, disp=-1)
        #
        print_process('Producing Summary of the Model')
        print model_res.summary()
        #
        print_process('Saving Model')
        model_name = str(model_res.__class__).strip("'>").split('.')[-1]
        path_to_model = '../saved_models/'+self.household_id+'_'+model_name+'.pkl'
        with open(path_to_model, 'w') as f:
            pickle.dump(model_res, f)
        print 'Model saved into the file: {}'.format(path_to_model)
        print
        print 'To run model and make predictions type in command line:'
        print 'python simple_main.py predict {} {}'.format(self.household_id, model_name)
        print
        #
        plt.plot(df_train)
        plt.plot(model_res.fittedvalues, color='g')
        plt.show()
        return model_res
