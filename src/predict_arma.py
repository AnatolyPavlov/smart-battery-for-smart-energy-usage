'''This module is for making predictions for trained models'''
import pandas as pd
import pyflux as pf
import cPickle as pickle
from sklearn.metrics import mean_squared_error, r2_score

# Custom Modules:
from auxiliary_functions import plot_pred_test, extract_days


class PredDataTimeIntervARMA(object):

    def __init__(self, environment_params):
        self.environment_params = environment_params

    def predict(self, df):
        num_days_pred = int(self.environment_params['num_days_pred'].values[0])
        if num_days_pred < 1:
            num_days_pred = 1
            print 'num_days_pred in ../params/environment_params.txt should be set to minimum of 1 day!'
            print
        household_id = self.environment_params['household_id'].values[0]
        train_days = str(self.environment_params['train_days'].values[0])
        part_of_week = self.environment_params['part_of_week'].values[0]
        #
        # Load and unpack models
        path_to_models =\
        '../saved_models/'+household_id+'_DataTimeIntervARMA_'+part_of_week+'_'+train_days+'.pkl'
        with open(path_to_models) as f_un:
            models = pickle.load(f_un)
        #
        # Making predictions
        df_pred = pd.DataFrame()
        for time_intv in models.keys():
            pred = models[time_intv].predict(h=num_days_pred)[df.columns[0]]
            df_dummy = pd.DataFrame(pred.values, columns=[df.columns[0]], index=pred.index)
            df_pred = df_pred.append(df_dummy)
        df_pred.sort_index(inplace=True, kind='mergesort')
        #
        days = extract_days(df)
        first_day_to_pred = days[0]
        last_day_to_pred = days[num_days_pred]
        df_test_days = df.query('index >= @first_day_to_pred and index < @last_day_to_pred')
        df_pred = pd.DataFrame(df_pred.values, columns=[df.columns[0]], index=df_test_days.index)
        #
        # Saving predicted and test days
        path_to_pred = \
        '../predictions/'+household_id+'_DataTimeIntervARMA_'+part_of_week+'_'+train_days+'.csv'
        df_pred.to_csv(path_to_pred)
        #
        path_to_test =\
        '../predictions/'+household_id+'_test_'+part_of_week+'_'+train_days+'.csv'
        df_test_days.to_csv(path_to_test)
        print 'Predictions saved into: {}'.format(path_to_pred)
        print
        #
        # Computing scores for predicted and test data and displaying them
        print 'Score of DataTimeIntervARMA: MSE = {}'\
        .format(mean_squared_error(df_test_days.values, df_pred.values))
        print 'Score of DataTimeIntervARMA: R^2 = {}'\
        .format(r2_score(df_test_days.values, df_pred.values))
        print '-----------------------------------------------------------------------------------'
        #
        # Plotting prediction and test day data
        plot_pred_test(df_test_days, df_pred, first_day_to_pred, 'DataTimeIntervARMA', self.environment_params)

if __name__ == '__main__':
    environment_params = pd.read_csv('../params/environment_params.txt', delim_whitespace=True)
    household_id = environment_params['household_id'].values[0]
    train_days = str(environment_params['train_days'].values[0])
    part_of_week = environment_params['part_of_week'].values[0]
    #
    path_to_test_data = '../clean_data/'+household_id+'_test_'+part_of_week+'_'+train_days+'.csv'
    df_test = pd.read_csv(path_to_test_data, parse_dates=True, index_col='Unnamed: 0')
    #
    pdtia = PredDataTimeIntervARMA(environment_params)
    pdtia.predict(df_test, 2)
