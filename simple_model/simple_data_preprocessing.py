'''This module contains methods for data preprocessing to apply to the data
before using it to train a model. It is designed to pre-process data of London
household smart meters readings of electric power consomption. Final if all
methods were applyed is the time series as pandas pd.DataFrame object, where
date-time stamp will be the index of the pd.DataFrame while corresponding
measurements of the power set as values in a single column in the pd.DataFrame.'''

import pandas as pd
from datetime import timedelta
#from collections import Counter
pd.options.mode.chained_assignment = None

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
        df_out = df.drop_duplicates(subset=self.datetime_col, keep='first')
        return df_out

    def drop_missing_val(self, df):
        df_out = df.dropna(how='any', subset=[self.yt_col], thresh=1)
        return df_out

    def drop_null_val(self, df):
        df_out = df.loc[df[self.yt_col] != 0]
        return df_out

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
                daytimes_indexes.append(df.index[i])
        df_out = df.drop(daytimes_indexes)
        return df_out

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
