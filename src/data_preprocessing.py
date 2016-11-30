'''This module contains methods for data preprocessing to apply to the data
before using it to train a model. It is designed to pre-process data of London
household smart meters readings of electric power consumption. Finally if all
methods were applied the data saved as time series pandas pd.DataFrame object, where
date-time stamp will be the index of the pd.DataFrame while corresponding
measurements of the power set as values in a single column in the pd.DataFrame.'''

import pandas as pd
from datetime import timedelta

# Custom Modules:
from auxiliary_functions import extract_days

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

    def transform(self, df):
        # Dropping duplicate records
        df = df.drop_duplicates(subset=self.datetime_col, keep='first')
        #
        # Dropping missing values
        df = df.dropna(how='any', subset=[self.yt_col], thresh=1)
        #
        # Dropping null values
        return df.loc[df[self.yt_col] != 0]

class DropIncompleteDays(object):

    def __init__(self, datetime_col, num_records_aday):
        self.datetime_col = datetime_col
        self.num_records_aday = num_records_aday

    def transform(self, df):
        days = extract_days(df, self.datetime_col)
        #
        days_to_drop = []
        datetimes = pd.to_datetime(df[self.datetime_col])
        for i, day in enumerate(days):
            next_day = day + timedelta(days=1)
            df_day = df[(datetimes >= day) & (datetimes < next_day)]
            if len(df_day) < self.num_records_aday:
                days_to_drop.append(day)

        daytimes_indexes = []
        for i, datetime in enumerate(datetimes):
            if datetime.date() in days_to_drop:
                daytimes_indexes.append(df.index[i])
        return df.drop(daytimes_indexes)

class ExtractTimeSeries(object):

    def __init__(self, datetime_col, yt_col):
        self.datetime_col = datetime_col
        self.yt_col = yt_col

    def transform(self, df):
        df[self.datetime_col] = pd.Series(pd.to_datetime(df[self.datetime_col]),\
        index=df.index)
        df = pd.DataFrame(df[self.yt_col].values, columns=[self.yt_col],\
                                    index=df[self.datetime_col].values)
        return df
