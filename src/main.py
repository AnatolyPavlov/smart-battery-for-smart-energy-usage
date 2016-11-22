'''This is the main module which makes calls to functions in different
modules and runs them in the order specified. This module also
loads row data and saves post-processed data predictions.'''

''' To run this module, type in the command line the following depending on
what do you want to do:

To run data preprocessing: python main.py data

To train model: python main.py model

To run optimization: python main.py opt
'''
import sys
import pandas as pd

# Custom Modules:
from auxiliary_functions import print_process
from data_preprocessing import ChooseHousehold, ConvertStrFloat,\
CleanData, ExtractTimeSeries

from feature_engineering import SplitWeek, TimeSeriesDataSplit
from model_arma import DataTimeIntvrvARMA, PriceCorrARMA
from optimization import run_optimization


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'To run code correctly enter in command line:'
        print 'python main.py <action> <household_id>'
    else:
        action = sys.argv[1]
        environment_params = pd.read_csv('../params/environment_params.txt', delim_whitespace=True)
        household_id = environment_params['household_id'].values[0]
        if action == 'data':
            path_data =\
            '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_1.csv'
            #
            print_process('Loading Data')
            df = pd.read_csv(path_data)
            #
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
            #
            path_to_clean_data = '../clean_data/'+household_id+'.csv'
            df.to_csv(path_to_clean_data)
            print_process('Clean data saved in: {}'.format(path_to_clean_data))
#=============================================================================================
        if action == 'model':
            path_to_clean_data = '../clean_data/'+household_id+'.csv'
            print_process('Loading Postprocessed Data')
            df = pd.read_csv(path_to_clean_data, parse_dates=True, index_col='Unnamed: 0')
            #
            print_process('Engineering Features')
            sp = SplitWeek(environment_params)
            df = sp.transform(df)
            #
            print_process('Splitting Data into Train and Test Subsets')
            tsds = TimeSeriesDataSplit(environment_params)
            df_train, df_test = tsds.train_test_split(df)
            #
            print_process('Training Data Time Intvrvals ARMA Model')
            dtiarma = DataTimeIntvrvARMA(environment_params)
            dtiarma.fit(df_train)
            print_process('Making predictions for Data Time Intvrvals ARMA Model')
            dtiarma.predict(df_test)
            #
            '''print_process('Training Price Correlated ARMA Model')
            pcarma =PriceCorrARMA(environment_params)
            pcarma.fit(df_train, df_test)
            pcarma.predict()'''
#=============================================================================================
        if action == 'opt':
            model_name = environment_params['model_name'].values[0]
            print_process('Optimization for '+model_name+' Model Predictions')
            run_optimization(environment_params)
