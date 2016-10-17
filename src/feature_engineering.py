

import pandas as pd
from collections import defaultdict
from datetime import timedelta

# Custom Modules:
from auxiliary_functions import print_process

class TimeSeriesDataSplit(object):

    def __init__(self, household_id, train_days):
        self.train_days = train_days
        self.household_id = household_id

    def train_test_split(self, df):
        if self.train_days < 1:
            print 'There must be at least one day in training set!'
            return
        days = []
        for i, datetime in enumerate(df.index):
            if datetime.date() not in days:
                days.append(datetime.date())
        print '{}th day: {}'.format(self.train_days, days[self.train_days-1])
        self.test_set_first_date = days[self.train_days]
        #
        df_train = df.query('index < @self.test_set_first_date')
        df_test = df.query('index >= @self.test_set_first_date')
        print
        print 'Training data set'
        print df_train.head()
        print df_train.tail()
        print
        print 'Test data set'
        print df_test.head()
        print df_test.tail()
        print_process('Saving Train and Test Data')
        path_to_train_data = '../clean_data/'+self.household_id+'_train.csv'
        path_to_test_data = '../clean_data/'+self.household_id+'_test.csv'
        df_train.to_csv(path_to_train_data)
        df_test.to_csv(path_to_test_data)
        print 'Train data saved into: {}'.format(path_to_train_data)
        print 'Test data saved into: {}'.format(path_to_test_data)
        return df_train, df_test

class SplitWeek(object):
    '''This class splits time series data
    into two subsets grouped by weekday and weekend.'''

    def __init__(self):
        self.part_of_week = None

    def transform(self, df):
        temp = pd.DatetimeIndex(df.index)
        df['weekday'] = temp.weekday
        df_weekdays = df[df['weekday'] <= 4].drop('weekday', axis=1)
        df_weekends = df[df['weekday'] > 4].drop('weekday', axis=1)
        print 'weekdays: {}, weekends: {}'.format(len(df_weekdays)/48, len(df_weekends)/48)
        print
        print 'Please enter a key word to specify what data to use to train model.'
        self.part_of_week =\
        raw_input("Enter: weekdays/weekends or press any key to train on entire data set:")
        #
        if self.part_of_week == 'weekdays':
            print
            print 'Selected weekdays only'
            return df_weekdays
        elif self.part_of_week == 'weekends':
            print
            print 'Selected weekends only'
            return df_weekends
        else:
            print
            print 'Selected all days of week'
            return df.drop('weekday', axis=1)

class ModelsTimeSlices(object):

    def transform(self, df):
        '''Transform input
        time series into a set of time series for
        each hourly-slice in a day, where each time
        series for a given hour has days as its agument.'''
        days = []
        for i, datetime in enumerate(df.index):
            if datetime.date() not in days:
                days.append(datetime.date())
        #
        day = days[0]
        next_day = day + timedelta(days=1)
        hours_in_day = []
        for i, datetime in enumerate(df.query('index >= @day and index < @next_day').index):
            if datetime.time() not in hours_in_day:
                hours_in_day.append(datetime.time())
        #
        df['time'] = [d.time() for i, d in enumerate(df.index)]
        houry_sliced_data = {} # key=hour slice, values = pd.DataFrame with daily time series
        for hour in hours_in_day:
            houry_sliced_data[hour] = df[df['time']==hour].drop('time', axis=1)
        #
        return hours_in_day, houry_sliced_data

class ModelsCorrPrice(object):

    def __init__(self, price_file_name):
        self.path_to_price = '../clean_data/'+price_file_name+'.csv'

    def transform(self, df, test_data=False):
        ''' transf '''
        days = []
        for i, datetime in enumerate(df.index):
            if datetime.date() not in days:
                days.append(datetime.date())
        #
        day = days[0]
        next_day = day + timedelta(days=1)
        hours_in_day = []
        for i, datetime in enumerate(df.query('index >= @day and index < @next_day').index):
            if datetime.time() not in hours_in_day:
                hours_in_day.append(datetime.time())
        #
        price = pd.read_csv(self.path_to_price, parse_dates=True, index_col='Unnamed: 0')
        prices_unique = price[price.columns[0]].unique()
        times_corr_by_price = defaultdict(list) # key=price, val=list of times for that price
        for i, pr in enumerate(price[price.columns[0]]):
            if pr in prices_unique:
                times_corr_by_price[pr].append(price.index[i].time())
        #
        df['time'] = [d.time() for i, d in enumerate(df.index)]
        price_corr_data = {}
        for pr, times in times_corr_by_price.iteritems():
            price_corr_data[pr] =\
            {time: df[df['time']==time].drop('time', axis=1)[df.columns[0]].values for time in times}

        data_means_grouped_by_price = {}
        for pr, data in price_corr_data.iteritems():
            data_means_grouped_by_price[pr] = pd.DataFrame(pd.DataFrame(data).mean(axis=1).values,\
            columns=[df.columns[0]], index=days)
        #
        if test_data:
            return data_means_grouped_by_price
        return prices_unique, data_means_grouped_by_price, times_corr_by_price
