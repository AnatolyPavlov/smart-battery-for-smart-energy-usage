'''This module contains methods for data preprocessing to apply to the data
before using it to train a model. It is designed to pre-process data of London
household smart meters readings of electric power consomption. The output of
the pipeline will be the time series as pandas pd.DataFrame object, where date-time
stamp will be the index of the pd.DataFrame while corresponding measurements
of the power set as values in a single column in the pd.DataFrame object.'''

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline, make_pipeline
from datetime import timedelta
from collections import Counter

pd.options.mode.chained_assignment = None

def show_households(df):
    print
    print 'All households in this subset of data:'
    print df['LCLid'].unique()
    print
    print 'Total number of households: {}'.format(len(df['LCLid'].unique()))
    print
    return df['LCLid'].unique()

def find_all_indexes(lst, item):
    return [i for i, x in enumerate(lst) if x==item]

def show_days_details(df, day_index=0):
    datetimes = df.index
    days = []
    for i, datetime in enumerate(datetimes):
        if datetime.date() not in days:
            days.append(datetime.date())

    print 'Printing days where number of records is not 48.'
    print
    for i, day in enumerate(days):
        next_day = day + timedelta(days=1)
        df_day = df.query('index >= @day and index < @next_day')
        if len(df_day) != 48:
            print '{}, {}, {}'.format(i, day, len(df_day))
    print
    print 'Total number of days for this household: {}'.format(len(days))
    print

    # show a single day time-series
    day = days[day_index]
    next_day = day + timedelta(days=1)
    df_day = df.query('index >= @day and index < @next_day')
    print
    print 'Time-series for {}. Todal number of records: {}'.format(day, len(df_day))
    print
    print df_day

#========================================================================================
class ChooseHousehold(object):

    def __init__(self, household_id=None):
        self.household_id = household_id

    def transform(self, df):
        if self.household_id == None or self.household_id not in df['LCLid'].unique():
            self.household_id = df['LCLid'].unique()[0]
        return df[df['LCLid']==self.household_id]

class ConvertStrFloat(object):

    def __init__(self, col_name):
        self.col_name = col_name

    def transform(self, df):
        pd.to_numeric(df[self.col_name], errors='ignore')
        df[self.col_name] = pd.to_numeric(df[self.col_name], errors='coerce')
        return df

class CleanData(object):

    def __init__(self, datetime_col, yt_col):
        self.datetime_col = datetime_col
        self.yt_col = yt_col

    def drop_duplicate_records(self, df):
        df.drop_duplicates(subset=self.datetime_col, keep='first', inplace=True)

    def drop_missing_val(self, df):
        df.dropna(how='any', subset=[self.yt_col], thresh=1, inplace=True)

    def drop_incomplete_days(self, df):
        datetimes = pd.to_datetime(df[self.datetime_col]) 
        days = []
        for i, datetime in enumerate(datetimes):
            if datetime.date() not in days:
                days.append(datetime.date())
        #
        days_to_drop = []
        for i, day in enumerate(days):
            next_day = day + timedelta(days=1)
            df_day = df[(datetimes >= day) & (datetimes < next_day)]
            if len(df_day) < 48:
                days_to_drop.append(day)

        daytimes_indexes = []
        for i, datetime in enumerate(datetimes):
            if datetime.date() in days_to_drop:
                #print ' index: {}, datetime: {}'.format(df.index[i], datetime.date())
                daytimes_indexes.append(df.index[i])
        df.drop(daytimes_indexes, inplace=True)

class ExtractTimeSeries(object):

    def __init__(self, datetime_col, yt_col):
        self.datetime_col = datetime_col
        self.yt_col = yt_col

    def transform(self, df):
        df[self.datetime_col] = pd.Series(pd.to_datetime(df[self.datetime_col]),\
        index=df.index)
        df_out = pd.DataFrame(df[self.yt_col].values, columns=[self.yt_col],\
                                    index=df[self.datetime_col].values)
        return df_out


if __name__ == '__main__':
    path_data =\
    '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_1.csv'
    path_data2 =\
    '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_2.csv'
    df = pd.read_csv(path_data)
    households = show_households(df)
    household = households[28]

    ch = ChooseHousehold(household)
    df = ch.transform(df)
    #
    csf = ConvertStrFloat('KWH/hh (per half hour) ')
    df = csf.transform(df)
    #
    cd = CleanData(datetime_col='DateTime', yt_col='KWH/hh (per half hour) ')
    cd.drop_duplicate_records(df)
    cd.drop_missing_val(df)
    cd.drop_incomplete_days(df)


    #
    ets = ExtractTimeSeries(datetime_col='DateTime', yt_col='KWH/hh (per half hour) ')
    df = ets.transform(df)
    #
    show_days_details(df)
    print
    print 'Above results are for the household_id: {}'.format(household)
    '''print 'First and last 5 rows of time-series for the household_id: {}'.format(household)
    print df.head()
    print
    print df.tail()'''
