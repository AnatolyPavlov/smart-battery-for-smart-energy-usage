'''This module is for making predictions for trained models'''
import pandas as pd
import pyflux as pf
import cPickle as pickle

class PredDataTimeIntervARMA(object):

    def __init__(self, environment_params):
        self.environment_params = environment_params

    def predict(self):
        num_days_pred = int(self.environment_params['num_days_pred'].values[0])
        if num_days_pred < 1:
            num_days_pred = 1
            print 'num_days_pred in ../params/environment_params.txt should be set to minimum of 1 day!'
            print
        household_id = self.environment_params['household_id'].values[0]
        train_days = str(self.environment_params['train_days'].values[0])
        part_of_week = self.environment_params['part_of_week'].values[0]
        model_name = self.environment_params['model_name'].values[0]
        #
        # Load and unpack models
        path_to_models =\
        '../saved_models/'+household_id+'_'+model_name+'_'+part_of_week+'_'+train_days+'.pkl'
        with open(path_to_models) as f_un:
            models = pickle.load(f_un)
        #
        # Making predictions
        df_pred = pd.DataFrame()
        for time_intv in models.keys():
            pred = models[time_intv].predict(h=num_days_pred)
            df_dummy = pd.DataFrame(pred.values, columns=[pred.columns[0]], index=pred.index)
            df_pred = df_pred.append(df_dummy)
        df_pred.sort_index(inplace=True, kind='mergesort')
        return df_pred
