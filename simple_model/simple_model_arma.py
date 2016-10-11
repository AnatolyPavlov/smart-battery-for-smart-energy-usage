'''This module contains arma model. It takes post-processed data provided via
simple_main.py module, splits these data into training and validating subsets,
trains model on training data and validates on validation data set. It saves
trained model as .pkl file, so that it can be uploaded and used to make predictions
and/or test the model on test data set.'''

import pandas as pd
import sys
import statsmodels.api as sm
from statsmodels.tsa.arima_process import arma_generate_sample

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
        return model_res


if __name__ == '__main__':
    path_to_clean_data = sys.argv[1]
    print
    print '## Loading Postprocessed Data'
    print
    df = pd.read_csv(path_to_clean_data)
    cols = df.columns
    #
    df[cols[0]] = pd.Series(pd.to_datetime(df[cols[0]]),\
    index=df.index)
    df = pd.DataFrame(df[cols[1]].values, columns=[cols[1]],\
    index=df[cols[0]].values)
    #
    print
    print '## Splitting Data into Train and Test Subsets'
    print
    tsds = TimeSeriesDataSplit('2013-06-22')
    df_train, df_test = tsds.train_test_split(df)
    print
    print 'Training data set'
    print df_train.head()
    print df_train.tail()
    print
    print 'Test data set'
    print df_test.head()
    print df_test.tail()
    print
    #
    print
    print '## Training Model'
    print
    marma = ModelARMA(p=7, q=7, freq='30Min')
    result = marma.fit(df_train)
