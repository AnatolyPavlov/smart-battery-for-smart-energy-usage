'''This is the main module which makes calls to functions in different
modules and runs them in the order specified. This module also
loads row data and saves post-processed data predictions.'''

''' To run this module, type in the command line the following depending on
what do you want to do:

To run data preprocessing: python main.py data <household_id>

To train model: python main.py model <household_id>
To train model and run optimization: python main.py model_opt <household_id>
'''

import sys
import pandas as pd
import numpy as np

# Custom Modules:
from auxiliary_functions import print_process
from data_preprocessing import ChooseHousehold, ConvertStrFloat,\
CleanData, ExtractTimeSeries

from feature_engineering import SplitWeek, TimeSeriesDataSplit
from model_arma import HourlyARMA, PriceCorrARMA
from optimization import run_optimization


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'To run code correctly enter in command line:'
        print 'python main.py <action> <household_id>'
    else:
        action = sys.argv[1]
        household_id = sys.argv[2]
        if action == 'data':
            path_data =\
            '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_1.csv'

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
            print 'python main.py model {}'.format(household_id)
            print
            print 'To train model and run optimization type:'
            print 'python main.py model_opt {}'.format(household_id)
            print
            print 'To train model for an other household type in command line:'
            print 'python main.py model <household_id>'
            print
#=============================================================================================
        if action == 'model' or action == 'model_opt':
            path_to_clean_data = '../clean_data/'+household_id+'.csv'
            print_process('Loading Postprocessed Data')
            df = pd.read_csv(path_to_clean_data, parse_dates=True, index_col='Unnamed: 0')
            #
            print_process('Engineering Features')
            sp = SplitWeek()
            df = sp.transform(df)
            #
            print_process('Splitting Data into Train and Test Subsets')
            train_days = raw_input('Enter number of days to train model on: ')
            tsds = TimeSeriesDataSplit(household_id, sp.part_of_week, int(train_days))
            df_train, df_test = tsds.train_test_split(df)
            #
            print_process('Training Hourly ARMA Model')
            harma = HourlyARMA(household_id, sp.part_of_week, train_days)
            harma.fit(df_train, df_test)
            harma.predict(df_test)
            #
            print_process('Training Price Correlated ARMA Model')
            price_file_name = raw_input('Enter price file name without extention: ')
            pcarma =\
            PriceCorrARMA(price_file_name, household_id, sp.part_of_week, train_days)
            pcarma.fit(df_train, df_test)
            pcarma.predict()
            #
            if action == 'model_opt':
                price_file_name = raw_input('Enter price file name without extention: ')
                print_process('Optimization for HourlyARMA Model Predictions')
                run_optimization(train_days, price_file_name, 'HourlyARMA', sp.part_of_week, household_id)
                #
                print_process('Optimization for PriceCorrARMA Model Predictions')
                run_optimization(train_days, pcarma.price_file_name, 'PriceCorrARMA', sp.part_of_week, household_id)
