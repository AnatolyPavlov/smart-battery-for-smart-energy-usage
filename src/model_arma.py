


import pandas as pd
import pyflux as pf
from datetime import timedelta
from sklearn.metrics import mean_squared_error, r2_score

# Custom Modules:
from feature_engineering import ModelsTimeSlices, ModelsCorrPrice
from auxiliary_functions import plot_pred_test

class HourlyARMA(object):

    def __init__(self, environment_params):
        self.environment_params = environment_params
        self.part_of_week = self.environment_params['part_of_week'].values[0]
        #
        self._models = dict()
        self.df_pred = pd.DataFrame()
        self.path_to_test = None
        self.path_to_pred = None
        self._score = list()

    def fit(self, df, df_test):
        '''The first step is to prepare data
        for multimodel training.'''
        mts = ModelsTimeSlices()
        hours_in_day, houry_sliced_data = mts.transform(df)
        #
        '''Now data ready to be sent for training models for each hourly slice'''
        p = 7
        q = 7
        if self.part_of_week == 'weekdays':
            p = 5
            q = 5
        elif self.part_of_week == 'weekends':
            p = 2
            q = 2
        #
        pred = []
        date = []
        time = []
        day_to_pred = df_test.index[0].date()
        for hour in hours_in_day:
            model=\
            pf.ARIMA(data=houry_sliced_data[hour], ar=p, ma=q, target=df.columns[0])
            self._models[hour] = model.fit("MLE")
            pred.append(model.predict(h=1)[df.columns[0]][0])
            date.append(str(day_to_pred))
            time.append(str(hour))
        self.df_pred = pd.DataFrame({'date': date, 'time': time, df.columns[0]: pred})
        idx = pd.to_datetime(self.df_pred['date'] + ' ' + self.df_pred['time'])
        self.df_pred =\
        pd.DataFrame(self.df_pred[df.columns[0]].values, columns=[df.columns[0]], index=idx)

    def predict(self, df):
        household_id = self.environment_params['household_id'].values[0]
        train_days = str(self.environment_params['train_days'].values[0])
        #
        day_to_pred = df.index[0].date()
        next_day = day_to_pred + timedelta(days=1)
        df_test_day = df.query('index >= @day_to_pred and index < @next_day')
        path_to_test =\
        '../predictions/'+household_id+'_test_'+self.part_of_week+'_'+train_days+'.csv'
        df_test_day.to_csv(path_to_test)
        #
        self._score.append(mean_squared_error(df_test_day.values, self.df_pred.values))
        self._score.append(r2_score(df_test_day.values, self.df_pred.values))
        print
        print 'Score of HourlyARMA: MSE = {}'.format(self._score[0])
        print 'Score of HourlyARMA: R^2 = {}'.format(self._score[1])
        print
        #
        path_to_pred = \
        '../predictions/'+household_id+'_HourlyARMA_'+self.part_of_week+'_'+train_days+'.csv'
        self.df_pred.to_csv(path_to_pred)
        print 'Predictions saved into: {}'.format(path_to_pred)
        print
        print 'The model HourlyARMA was trained for the following set of parameters:'
        print 'household_id: {}, part of week: {}, number of train days: {}'\
        .format(household_id, self.part_of_week, train_days)
        print '-----------------------------------------------------------------------------------'
        #
        plot_pred_test(df_test_day, self.df_pred, day_to_pred, 'HourlyARMA', self.part_of_week, household_id, train_days)

class PriceCorrARMA(object):

    def __init__(self, environment_params):
        self.environment_params = environment_params
        self.household_id = self.environment_params['household_id'].values[0]
        self.part_of_week = self.environment_params['part_of_week'].values[0]
        self.train_days = str(self.environment_params['train_days'].values[0])
        self.price_file_name = self.environment_params['price_file_name'].values[0]
        #
        self._models = dict()
        self.df_pred = pd.DataFrame()
        self.df_test_day = pd.DataFrame()
        self.path_to_test = None
        self.path_to_pred = None
        self._score = list()

    def fit(self, df, df_test):
        '''The first step is to prepare data
        for multimodel training.'''
        mcp = ModelsCorrPrice(self.price_file_name)
        prices_unique, data_means_grouped_by_price, times_corr_by_price = mcp.transform(df)
        #
        day_to_pred = df_test.index[0].date()
        next_day = day_to_pred + timedelta(days=1)
        self.df_test_day = df_test.query('index >= @day_to_pred and index < @next_day')
        path_to_test =\
        '../predictions/'+self.household_id+'_test_'+self.part_of_week+'_'+self.train_days+'.csv'
        self.df_test_day.to_csv(path_to_test)
        self.path_to_test = path_to_test
        #
        dummy_test = mcp.transform(self.df_test_day, test_data=True)
        #
        '''Now data ready to be sent for training models for each hourly slice'''
        p = 8
        q = 8
        if self.part_of_week == 'weekdays':
            p = 6
            q = 6
        elif self.part_of_week == 'weekends':
            p = 3
            q = 3
        #
        dummy_pred = {}
        for pr in prices_unique:
            model=\
            pf.ARIMA(data=data_means_grouped_by_price[pr], ar=p, ma=q, target=df.columns[0])
            self._models[pr] = model.fit("MLE")
            dummy_pred[pr] = model.predict(h=1)[df.columns[0]][0]
            #
            dummy_test[pr] = dummy_test[pr].values[0][0]
        #
        date = []
        time_pred = []
        time_test = []
        for pr in prices_unique:
            for time in times_corr_by_price[pr]:
                time_pred.append((time, dummy_pred[pr]))
                time_test.append((time, dummy_test[pr]))
                date.append(str(day_to_pred))
        #
        ttime, test = zip(*sorted(time_test, key=lambda tup: tup[0]))
        time, pred = zip(*sorted(time_pred, key=lambda tup: tup[0]))
        time = [str(t) for t in time]
        self.df_test_day = pd.DataFrame({'date': date, 'time': time, df.columns[0]: test})
        self.df_pred = pd.DataFrame({'date': date, 'time': time, df.columns[0]: pred})
        idx = pd.to_datetime(self.df_pred['date'] + ' ' + self.df_pred['time'])
        self.df_pred =\
        pd.DataFrame(self.df_pred[df.columns[0]].values, columns=[df.columns[0]], index=idx)
        self.df_test_day =\
        pd.DataFrame(self.df_test_day[df.columns[0]].values, columns=[df.columns[0]], index=idx)

    def predict(self):
        day_to_pred = self.df_test_day.index[0].date()
        #
        self._score.append(mean_squared_error(self.df_test_day.values, self.df_pred.values))
        self._score.append(r2_score(self.df_test_day.values, self.df_pred.values))
        print
        print 'Score of PriceCorrARMA: MSE = {}'.format(self._score[0])
        print 'Score of PriceCorrARMA: R^2 = {}'.format(self._score[1])
        print
        #
        path_to_pred = \
        '../predictions/'+self.household_id+'_PriceCorrARMA_'+self.part_of_week+'_'+self.train_days+'.csv'
        self.df_pred.to_csv(path_to_pred)
        self.path_to_pred = path_to_pred
        print 'Predictions saved into: {}'.format(path_to_pred)
        print
        print 'The model PriceCorrARMA was trained for the following set of parameters:'
        print 'household_id: {}, part of week: {}, number of train days: {}, price file name: {}'\
        .format(self.household_id, self.part_of_week, self.train_days, self.price_file_name)
        print '-----------------------------------------------------------------------------------'
        #
        plot_pred_test(self.df_test_day, self.df_pred, day_to_pred, 'PriceCorrARMA', self.part_of_week, self.household_id, self.train_days)
