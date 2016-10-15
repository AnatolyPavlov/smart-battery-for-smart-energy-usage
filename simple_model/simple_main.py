'''This is the main module which makes calls to functions in defferent
modules and runs them in order specified in this module. This module also
loads row data and outputs, if it is directed so, post-processed data and
it also saves the model in .pkl file.'''

''' To run this module, type in command line the following depending on
what do you want to do:

To run data preprocessing: python simple_main.py data <household_id>

To plot ACF and PACF graph to help in chosing p and q parameters to
train model with, type: python simple_main.py ACF_PACF <household_id>

To train model: python simple_main.py model <household_id>

To run model for testing or predicting:
python simple_main.py predict <household_id> <model_name>
'''

import sys
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from datetime import timedelta

# Custom Modules:
from auxiliary_functions import print_process, plot_acf_pacf
from simple_data_preprocessing import ChooseHousehold, ConvertStrFloat,\
CleanData, ExtractTimeSeries

from simple_model_arma import TimeSeriesDataSplit, ModelARMA
from simple_predict import PredictARMA
from model_arma import EnsembleARMA, PriceCorrARMA


if __name__ == '__main__':
    action = sys.argv[1]
    household_id = sys.argv[2]
    if action == 'data':
        path_data =\
        '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_1.csv'
        path_data2 =\
        '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_2.csv'

        print_process('Loading Data')
        df = pd.read_csv(path_data)

        print_process('Data Preprocessing')
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
        print_process('Saving Data')
        path_to_clean_data = '../clean_data/'+household_id+'.csv'
        df.to_csv(path_to_clean_data)
        print 'Clean data saved in: {}'.format(path_to_clean_data)
        print
        print 'To train model for this particular household type in command line:'
        print 'python simple_main.py model {}'.format(household_id)
        print
        print 'To train model for an other household type in command line:'
        print 'python simple_main.py model <household_id>'
        print
#=============================================================================================
    if action == 'ACF_PACF':
        path_to_clean_data = '../clean_data/'+household_id+'.csv'
        print_process('Loading Postprocessed Data')
        df = pd.read_csv(path_to_clean_data, parse_dates=True, index_col='Unnamed: 0')
        #
        plot_acf_pacf(df, 24)
#=============================================================================================
    if action == 'model':
        path_to_clean_data = '../clean_data/'+household_id+'.csv'
        print_process('Loading Postprocessed Data')
        df = pd.read_csv(path_to_clean_data, parse_dates=True, index_col='Unnamed: 0')
        #
        print_process('Splitting Data into Train and Test Subsets')
        tsds = TimeSeriesDataSplit(household_id=household_id, train_days=10)
        df_train, df_test = tsds.train_test_split(df)
        #
        print_process('Training Model')
        earma = EnsembleARMA(household_id=household_id, p=1, q=1)
        earma.fit(df_train)
        pred = earma.predict(df_test)
        #marma = ModelARMA(household_id=household_id, p=4, q=3, trend='nc', freq='30Min').fit(df_train)
        pcarma = PriceCorrARMA(price_file_name='price_data_London', household_id=household_id, p=1, q=1)
        pcarma.fit(df_train)
        pred2 = pcarma.predict(df_test)
#=============================================================================================
    if action == 'predict':
        model_name = sys.argv[3]
        path_to_test_data = '../clean_data/'+household_id+'_test.csv'
        path_to_model = '../saved_models/'+household_id+'_'+model_name+'.pkl'
        #path_to_train_data = sys.argv[4]
        print_process('Loading Test Data')
        df_test = pd.read_csv(path_to_test_data, parse_dates=True, index_col='Unnamed: 0')
        #
        parma = PredictARMA(household_id=household_id, model_name=model_name)
        y_pred = parma.predict(df_test)
        #
        parma.plot_pred_timeseries(df_test, y_pred)
