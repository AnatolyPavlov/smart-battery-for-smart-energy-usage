'''This module defines class for machine learning model.'''
import pandas as pd
import pyflux as pf
import cPickle as pickle

# Custom Modules:
from feature_engineering import ModelsDataTimeInterv, ModelsCorrPrice

class DataTimeIntervARMA(object):

    def __init__(self, environment_params):
        self.environment_params = environment_params

    def fit(self, time_intervs_data):
        part_of_week = self.environment_params['part_of_week'].values[0]
        household_id = self.environment_params['household_id'].values[0]
        train_days = str(self.environment_params['train_days'].values[0])
        model_name = self.environment_params['model_name'].values[0]
        #
        # Setting hyperparameters
        p = 7
        q = 7
        if part_of_week == 'weekdays':
            p = 5
            q = 5
        elif part_of_week == 'weekends':
            p = 2
            q = 2
        #
        # Training models for each time interval
        models = {}
        for time_intv in time_intervs_data.keys():
            model=\
            pf.ARIMA(data=time_intervs_data[time_intv], ar=p, ma=q, target=time_intervs_data[time_intv].columns[0])
            model.fit("MLE")
            models[time_intv] = model
            print '  Trained for the time interval: {}'.format(time_intv)
        print
        print 'The model {} was trained for the following set of parameters:'.format(model_name)
        print 'household_id: {}, part of week: {}, number of train days: {}'\
        .format(household_id, part_of_week, train_days)
        #
        # Saving models
        path_to_models =\
        '../saved_models/'+household_id+'_'+model_name+'_'+part_of_week+'_'+train_days+'.pkl'
        with open(path_to_models, 'w') as f:
            pickle.dump(models, f)
        print
        print 'The model was saved into: {}'.format(path_to_models)
