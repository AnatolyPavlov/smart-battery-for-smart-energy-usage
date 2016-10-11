'''This is the main module which makes calls to functions in defferent
modules and runs them in order specified in this module. This module also
loads row data and outputs, if it is directed so, post-processed data and
it also saves the model in .pkl file.'''

''' To run this module, type in command line the following depending on
what do you want to do:

To run data preprocessing: python simple_main.py data household_id

To plot ACF and PACF graph to help in chosing p and q parameters to
train model with, type: python simple_main.py ACF_PACF path_to_clean_data

To train model: python simple_main.py model path_to_clean_data

To run model for testing or predicting: python simple_main.py predict path_to_model path_to_test_data
'''

import sys
import pandas as pd
import cPickle as pickle
import matplotlib.pyplot as plt
from datetime import timedelta
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Custom Modules:
from simple_data_preprocessing import ChooseHousehold, ConvertStrFloat,\
CleanData, ExtractTimeSeries

from simple_model_arma import TimeSeriesDataSplit, ModelARMA

from simple_predict import PredictARMA

def plot_acf_pacf(df, lags):
   fig = plt.figure(figsize=(12,8))
   ax1 = fig.add_subplot(211)
   fig = plot_acf(df, lags=lags, ax=ax1)
   ax2 = fig.add_subplot(212)
   fig = plot_pacf(df, lags=lags, ax=ax2)
   plt.show()

if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'data':
        household_id = sys.argv[2]
        path_data =\
        '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_1.csv'
        path_data2 =\
        '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_2.csv'
        print
        print '## Loading Data'
        print
        df = pd.read_csv(path_data)

        print
        print '## Data Preprocessing'
        print
        ch = ChooseHousehold(household_id)
        df = ch.transform(df)
        #
        csf = ConvertStrFloat('KWH/hh (per half hour) ')
        df = csf.transform(df)
        #
        cd = CleanData(datetime_col='DateTime', yt_col='KWH/hh (per half hour) ')
        df = cd.drop_duplicate_records(df)
        df = cd.drop_missing_val(df)
        df = cd.drop_null_val(df)
        df = cd.drop_incomplete_days(df)
        #
        ets = ExtractTimeSeries(datetime_col='DateTime', yt_col='KWH/hh (per half hour) ')
        df = ets.transform(df)
        print
        print '## Saving Data'
        print
        path_to_clean_data = '../clean_data/'+household_id+'.csv'
        df.to_csv(path_to_clean_data)
        print 'Clean data saved in: {}'.format(path_to_clean_data)
        print
        print 'To train model type in command line:'
        print 'python simple_main.py model {}'.format(path_to_clean_data)
        print
#=============================================================================================
    if action == 'ACF_PACF':
        path_to_clean_data = sys.argv[2]
        print
        print '## Loading Postprocessed Data'
        print
        df = pd.read_csv(path_to_clean_data)
        #
        cols = df.columns
        ets = ExtractTimeSeries(datetime_col=cols[0], yt_col=cols[1])
        df = ets.transform(df)
        plot_acf_pacf(df, 24)
#=============================================================================================
    if action == 'model':
        path_to_clean_data = sys.argv[2]
        print
        print '## Loading Postprocessed Data'
        print
        df = pd.read_csv(path_to_clean_data)
        #
        cols = df.columns
        ets = ExtractTimeSeries(datetime_col=cols[0], yt_col=cols[1])
        df = ets.transform(df)
        #
        print
        print '## Splitting Data into Train and Test Subsets'
        print
        tsds = TimeSeriesDataSplit('2012-12-15')
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
        print
        print '## Saving Train and Test Data'
        print
        path_to_train_data = '../clean_data/df_train.csv'
        path_to_test_data = '../clean_data/df_test.csv'
        df_train.to_csv(path_to_train_data)
        df_test.to_csv(path_to_test_data)
        print 'Train data saved into: {}'.format(path_to_train_data)
        print 'Test data saved into: {}'.format(path_to_test_data)
        #
        print
        print '## Training Model'
        print
        marma = ModelARMA(p=2, q=2, freq='30Min').fit(df_train)
        #
        print
        print '## Saving Model'
        print
        class_name = str(marma.__class__).strip("'>").split('.')[-1]
        model_name = class_name+'.pkl'
        with open(model_name, 'w') as f:
            pickle.dump(marma, f)
        print 'Model saved into the file: {}'.format(model_name)
#=============================================================================================
    if action == 'predict':
        path_to_model = sys.argv[2]
        path_to_test_data = sys.argv[3]
        #path_to_train_data = sys.argv[4]
        print
        print '## Loading Test Data'
        print
        df_test = pd.read_csv(path_to_test_data)
        #
        cols = df_test.columns
        ets = ExtractTimeSeries(datetime_col=cols[0], yt_col=cols[1])
        df_test = ets.transform(df_test)
        #
        parma = PredictARMA(path_to_model)
        y_pred = parma.predict(df_test)
        #
        parma.plot_pred_timeseries(df_test, y_pred)
