'''This is the main module which makes calls to functions in different
modules and runs them in the order specified. This module also
loads row data and saves post-processed data predictions.'''

''' To run this module, type in the command line the following depending on
what do you want to do:

To run data preprocessing: python main.py data

To train model: python main.py model

To make predictions: python main.py pred

To run optimization: python main.py opt
'''
import sys
import pandas as pd

# Custom Modules:
from auxiliary_functions import print_process
from data_preprocessing import ChooseHousehold, ConvertStrFloat,\
CleanData, ExtractTimeSeries

from feature_engineering import SplitWeek, TimeSeriesDataSplit
from model_arma import DataTimeIntervARMA, PriceCorrARMA
from predict_arma import PredDataTimeIntervARMA
from optimization import run_optimization


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'To run code correctly enter in command line:'
        print 'python main.py <action> where action = {data, model, opt}'
    else:
        action = sys.argv[1]
        environment_params = pd.read_csv('../params/environment_params.txt', delim_whitespace=True)
        household_id = environment_params['household_id'].values[0]
        if action == 'data':
            file_num = raw_input('Enter the file number (1 to 168) whose data you want to preproces: ')
            path_to_data = '../data/Power-Networks-LCL-June2015(withAcornGps)v2_'+file_num+'.csv'
            #
            print_process('Loading Data')
            df = pd.read_csv(path_to_data)
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
            model_name = environment_params['model_name'].values[0]
            print_process('Training '+model_name+' Model')
            if model_name == 'DataTimeIntervARMA':
                dtiarma = DataTimeIntervARMA(environment_params)
                dtiarma.fit(df_train)
            #
            '''print_process('Training Price Correlated ARMA Model')
            pcarma = PriceCorrARMA(environment_params)
            pcarma.fit(df_train, df_test)
            pcarma.predict()'''
#=============================================================================================
        if action == 'pred':
            train_days = str(environment_params['train_days'].values[0])
            part_of_week = environment_params['part_of_week'].values[0]
            path_to_test_data = '../clean_data/'+household_id+'_test_'+part_of_week+'_'+train_days+'.csv'
            df_test = pd.read_csv(path_to_test_data, parse_dates=True, index_col='Unnamed: 0')
            #
            model_name = environment_params['model_name'].values[0]
            print_process('Making predictions from '+model_name+' Model')
            if model_name == 'DataTimeIntervARMA':
                pdtia = PredDataTimeIntervARMA(environment_params)
                pdtia.predict(df_test)
#=============================================================================================
        if action == 'opt':
            model_name = environment_params['model_name'].values[0]
            print_process('Optimization for '+model_name+' Model Predictions')
            run_optimization(environment_params)
