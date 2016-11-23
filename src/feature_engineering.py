

import pandas as pd
from collections import defaultdict
from datetime import timedelta

# Custom Modules:
from auxiliary_functions import print_process, extract_days

class SplitWeek(object):
    '''This class splits time series data
    into two subsets grouped by weekday and weekend.'''

    def __init__(self, environment_params):
        self.environment_params = environment_params

    def transform(self, df):
        temp = pd.DatetimeIndex(df.index)
        df['weekday'] = temp.weekday
        df_weekdays = df[df['weekday'] <= 4].drop('weekday', axis=1)
        weekdays = extract_days(df_weekdays)
        df_weekends = df[df['weekday'] > 4].drop('weekday', axis=1)
        weekends = extract_days(df_weekends)
        print 'weekdays: {}, weekends: {}'.format(len(weekdays), len(weekends))
        print
        part_of_week = self.environment_params['part_of_week'].values[0]
        #
        if part_of_week == 'weekdays':
            print
            print 'Selected weekdays only'
            return df_weekdays
        elif part_of_week == 'weekends':
            print
            print 'Selected weekends only'
            return df_weekends
        else:
            print
            print 'Selected all days of week'
            return df.drop('weekday', axis=1)


class TimeSeriesDataSplit(object):

    def __init__(self, environment_params):
        self.environment_params = environment_params

    def train_test_split(self, df):
        household_id = self.environment_params['household_id'].values[0]
        part_of_week = self.environment_params['part_of_week'].values[0]
        train_days = self.environment_params['train_days'].values[0]
        if train_days < 10:
            print 'There must be at least 10 days in training set!'
            return
        days = []
        for i, datetime in enumerate(df.index):
            if datetime.date() not in days:
                days.append(datetime.date())
        print '{}th day: {}'.format(train_days, days[train_days-1])
        test_set_first_date = days[train_days]
        #
        df_train = df.query('index < @test_set_first_date')
        df_test = df.query('index >= @test_set_first_date')
        print
        print 'Training data set'
        print df_train.head()
        print df_train.tail()
        print
        print 'Test data set'
        print df_test.head()
        print df_test.tail()
        print_process('Saving Train and Test Data')
        path_to_train_data = '../clean_data/'+household_id+'_train_'+part_of_week+'_'+str(train_days)+'.csv'
        path_to_test_data = '../clean_data/'+household_id+'_test_'+part_of_week+'_'+str(train_days)+'.csv'
        df_train.to_csv(path_to_train_data)
        df_test.to_csv(path_to_test_data)
        print 'Train data saved into: {}'.format(path_to_train_data)
        print 'Test data saved into: {}'.format(path_to_test_data)
        return df_train, df_test


class ModelsDataTimeInterv(object):

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
