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
from sklearn.metrics import mean_squared_error, r2_score

# Custom Modules:
from auxiliary_functions import print_process, plot_pred_test, extract_days
from data_preprocessing import ChooseHousehold, ConvertStrFloat,\
CleanData, DropIncompleteDays, ExtractTimeSeries

from feature_engineering import SplitWeek, TimeSeriesDataSplit,\
ModelsDataTimeInterv, ModelsCorrPrice
from model_arma import DataTimeIntervARMA
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
            df = cd.transform(df)
            #
            did = DropIncompleteDays(datetime_col='DateTime', num_records_aday=48)
            df = did.transform(df)
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
            sp = SplitWeek(environment_params)
            df = sp.transform(df)
            #
            print_process('Splitting Data into Train and Test Subsets')
            tsds = TimeSeriesDataSplit(environment_params)
            df_train, df_test = tsds.train_test_split(df)
            #
            model_name = environment_params['model_name'].values[0]
            if model_name == 'DataTimeIntervARMA':
                print_process('Engineering Features for '+model_name+' Model')
                mdti = ModelsDataTimeInterv()
                time_intervs_data = mdti.transform(df_train)
                #
                print_process('Training '+model_name+' Model')
                dtiarma = DataTimeIntervARMA(environment_params)
                dtiarma.fit(time_intervs_data)
            #
            if model_name == 'PriceCorrARMA':
                print_process('Engineering Features for '+model_name+' Model')
                price_file_name = environment_params['price_file_name'].values[0]
                mcp = ModelsCorrPrice(price_file_name)
                data_means_grouped_by_price = mcp.transform(df_train)
                #
                print_process('Training '+model_name+' Model')
                dtiarma = DataTimeIntervARMA(environment_params)
                dtiarma.fit(data_means_grouped_by_price)
#=============================================================================================
        if action == 'pred':
            model_name = environment_params['model_name'].values[0]
            print_process('Making predictions from '+model_name+' Model')
            pdtia = PredDataTimeIntervARMA(environment_params)
            df_pred = pdtia.predict()
            #
            # Loading test data and extracting only days specified to compare predictions with
            train_days = str(environment_params['train_days'].values[0])
            part_of_week = environment_params['part_of_week'].values[0]
            num_days_pred = environment_params['num_days_pred'].values[0]
            #
            path_to_test_data = '../clean_data/'+household_id+'_test_'+part_of_week+'_'+train_days+'.csv'
            df_test = pd.read_csv(path_to_test_data, parse_dates=True, index_col='Unnamed: 0')
            #
            days = extract_days(df_test)
            first_day_to_pred = days[0]
            last_day_to_pred = days[num_days_pred]
            df_test_days = df_test.query('index >= @first_day_to_pred and index < @last_day_to_pred')
            #
            if model_name == 'PriceCorrARMA':
                price_file_name = environment_params['price_file_name'].values[0]
                mcp = ModelsCorrPrice(price_file_name)
                df_pred = mcp.transform_inverse(df_pred)
                #
                df_test_days = mcp.transform(df_test_days, test_data=True)
                df_test_days = mcp.transform_inverse(df_test_days)
            #
            df_pred = pd.DataFrame(df_pred.values, columns=[df_pred.columns[0]], index=df_test_days.index)
            #
            # Saving predicted and test days
            path_to_pred = \
            '../predictions/'+household_id+'_'+model_name+'_'+part_of_week+'_'+train_days+'.csv'
            df_pred.to_csv(path_to_pred)
            #
            path_to_test =\
            '../predictions/'+household_id+'_test_'+part_of_week+'_'+train_days+'.csv'
            df_test_days.to_csv(path_to_test)
            print 'Predictions saved into: {}'.format(path_to_pred)
            print
            #
            # Computing scores for predicted and test data and displaying them
            print 'Score of {}: MSE = {}'\
            .format(model_name, mean_squared_error(df_test_days.values, df_pred.values))
            print 'Score of {}: R^2 = {}'\
            .format(model_name, r2_score(df_test_days.values, df_pred.values))
            print '-----------------------------------------------------------------------------------'
            #
            # Plotting prediction and test day data
            plot_pred_test(df_test_days, df_pred, first_day_to_pred, environment_params)
#=============================================================================================
        if action == 'opt':
            model_name = environment_params['model_name'].values[0]
            print_process('Optimization for '+model_name+' Model Predictions')
            run_optimization(environment_params)
