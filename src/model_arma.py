


import pandas as pd
import pyflux as pf
import matplotlib.pyplot as plt
from datetime import timedelta
from sklearn.metrics import mean_squared_error, r2_score

# Custom Modules:
from feature_engineering import ModelsTimeSlices, ModelsCorrPrice
from auxiliary_functions import plot_pred_test

class HourlyARMA(object):

    def __init__(self, household_id, part_of_week, train_days):
        self.household_id = household_id
        self.part_of_week = part_of_week
        self.train_days = train_days
        #
        self.p = 7
        self.q = 7
        if self.part_of_week == 'weekdays':
            self.p = 5
            self.q = 5
        elif self.part_of_week == 'weekends':
            self.p = 2
            self.q = 2
        else:
            self.part_of_week = 'all-days-week'
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
        pred = []
        date = []
        time = []
        day_to_pred = df_test.index[0].date()
        for hour in hours_in_day:
            model=\
            pf.ARIMA(data=houry_sliced_data[hour], ar=self.p, ma=self.q, target=df.columns[0])
            self._models[hour] = model.fit("MLE")
            pred.append(model.predict(h=1)[df.columns[0]][0])
            date.append(str(day_to_pred))
            time.append(str(hour))
        self.df_pred = pd.DataFrame({'date': date, 'time': time, df.columns[0]: pred})
        idx = pd.to_datetime(self.df_pred['date'] + ' ' + self.df_pred['time'])
        self.df_pred =\
        pd.DataFrame(self.df_pred[df.columns[0]].values, columns=[df.columns[0]], index=idx)

    def predict(self, df):
        day_to_pred = df.index[0].date()
        next_day = day_to_pred + timedelta(days=1)
        df_test_day = df.query('index >= @day_to_pred and index < @next_day')
        path_to_test =\
        '../predictions/'+self.household_id+'_test_'+self.part_of_week+'_'+str(self.train_days)+'.csv'
        df_test_day.to_csv(path_to_test)
        self.path_to_test = path_to_test
        #
        self._score.append(mean_squared_error(df_test_day.values, self.df_pred.values))
        self._score.append(r2_score(df_test_day.values, self.df_pred.values))
        print
        print 'Score of HourlyARMA: MSE = {}'.format(self._score[0])
        print 'Score of HourlyARMA: R^2 = {}'.format(self._score[1])
        print
        #
        path_to_pred = \
        '../predictions/'+self.household_id+'_HourlyARMA_'+self.part_of_week+'_'+str(self.train_days)+'.csv'
        self.df_pred.to_csv(path_to_pred)
        self.path_to_pred = path_to_pred
        print 'Predictions saved into: {}'.format(path_to_pred)
        print
        print 'To run optimization.py on predictions of HourlyARMA model use the following:'
        print 'household_id: {}, part of week: {}, number of train days: {}'\
        .format(self.household_id, self.part_of_week, self.train_days)
        print '-----------------------------------------------------------------------------------'
        #
        plot_pred_test(df_test_day, self.df_pred, day_to_pred, 'HourlyARMA', self.part_of_week, self.household_id, str(self.train_days))

class PriceCorrARMA(object):

    def __init__(self, price_file_name, household_id, part_of_week, train_days):
        self.price_file_name = price_file_name
        self.household_id = household_id
        self.part_of_week = part_of_week
        self.train_days = train_days
        #
        self.p = 8
        self.q = 8
        if self.part_of_week == 'weekdays':
            self.p = 6
            self.q = 6
        elif self.part_of_week == 'weekends':
            self.p = 3
            self.q = 3
        else:
            self.part_of_week = 'all-days-week'
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
        '../predictions/'+self.household_id+'_test_'+self.part_of_week+'_'+str(self.train_days)+'.csv'
        self.df_test_day.to_csv(path_to_test)
        self.path_to_test = path_to_test
        #
        dummy_test = mcp.transform(self.df_test_day, test_data=True)
        #
        '''Now data ready to be sent for training models for each hourly slice'''
        dummy_pred = {}
        for pr in prices_unique:
            model=\
            pf.ARIMA(data=data_means_grouped_by_price[pr], ar=self.p, ma=self.q, target=df.columns[0])
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
        '../predictions/'+self.household_id+'_PriceCorrARMA_'+self.part_of_week+'_'+str(self.train_days)+'.csv'
        self.df_pred.to_csv(path_to_pred)
        self.path_to_pred = path_to_pred
        print 'Predictions saved into: {}'.format(path_to_pred)
        print
        print 'To run optimization.py on predictions of PriceCorrARMA model use the following:'
        print 'household_id: {}, part of week: {}, number of train days: {}, price file name: {}'\
        .format(self.household_id, self.part_of_week, self.train_days, self.price_file_name)
        print '-----------------------------------------------------------------------------------'
        #
        plot_pred_test(self.df_test_day, self.df_pred, day_to_pred, 'PriceCorrARMA', self.part_of_week, self.household_id, str(self.train_days))
