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
        train_days = raw_input("Enter number of days to train model on:")
        train_days = int(train_days)
        tsds = TimeSeriesDataSplit(household_id=household_id, train_days=train_days)
        df_train, df_test = tsds.train_test_split(df)
        #
        print_process('Training Model')
        harma = HourlyARMA(household_id=household_id, part_of_week=sp.part_of_week)
        harma.fit(df_train, df_test)
        harma.predict(df_test)
        #marma = ModelARMA(household_id=household_id, p=4, q=3, trend='nc', freq='30Min').fit(df_train)
        pcarma =\
        PriceCorrARMA(price_file_name='price_data_London', household_id=household_id, part_of_week=sp.part_of_week)
        pcarma.fit(df_train, df_test)
        pcarma.predict()
        #
        if action == 'model_opt':
            print_process('Optimization for HourlyARMA Model Predictions')
            run_optimization(harma.path_to_pred, harma.path_to_test, pcarma.path_to_price)
            #
            print_process('Optimization for PriceCorrARMA Model Predictions')
            run_optimization(pcarma.path_to_pred, pcarma.path_to_test, pcarma.path_to_price)
