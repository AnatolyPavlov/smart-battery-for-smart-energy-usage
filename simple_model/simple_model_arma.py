'''This module contains arma model. It takes post-processed data provided via
simple_main.py module, splits these data into training and validating subsets,
trains model on training data and validates on validation data set. It saves
trained model as .pkl file, so that it can be uploaded and used to make predictions
and/or test the model on test data set.'''

import pandas as pd
import statsmodels.api as sm
import cPickle as pickle
import matplotlib.pyplot as plt

class TimeSeriesDataSplit(object):

    def __init__(self, test_set_first_date):
        '''INPUT: last date in training data subset.
        The type and format of date should be: str, yyyy-mm-dd
        for example: '2013-06-22' '''
        self.test_set_first_date = pd.to_datetime(test_set_first_date)
        self.test_set_first_date = self.test_set_first_date.date()

    def train_test_split(self, df):
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
        print
        print
        print '## Saving Train and Test Data'
        print
        path_to_train_data = '../clean_data/df_train.csv'
        path_to_test_data = '../clean_data/df_test.csv'
        df_train.to_csv(path_to_train_data)
        df_test.to_csv(path_to_test_data)
        print 'Train data saved into: {}'.format(path_to_train_data)
        print 'Test data saved into: {}'.format(path_to_test_data)
        return df_train, df_test

class ModelARMA(object):

    def __init__(self, p, q, freq=None):
        self.p = p
        self.q = q
        self.freq = freq

    def fit(self, df_train):
        model = sm.tsa.ARMA(df_train, order=(self.p, self.q), freq=self.freq)
        model_res = model.fit(trend='c',disp=-1)
        #
        print
        print '## Producing Summary of the Model'
        print
        print model_res.summary()
        #
        print
        print '## Saving Model'
        print
        model_name = str(model_res.__class__).strip("'>").split('.')[-1]
        path_to_model = '../saved_models/'+model_name+'.pkl'
        with open(path_to_model, 'w') as f:
            pickle.dump(model_res, f)
        print 'Model saved into the file: {}'.format(path_to_model)
        print
        print 'To run model and make predictions type in command line:'
        print 'python simple_main.py predict {} <path_to_test_data>'.format(path_to_model)
        print
        #
        plt.plot(df_train)
        plt.plot(model_res.fittedvalues, color='g')
        plt.show()
        return model_res
