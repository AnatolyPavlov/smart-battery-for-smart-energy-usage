'''This module contains methods for data preprocessing to apply to the data
before using it to train a model. It is designed to pre-process data of London
household smart meters readings of electric power consomption. The output of
the pipeline will be the time series as pandas pd.DataFrame object, where date-time
will be the index of the pd.DataFrame while corresponding measurements of the power
set as values in a single column in the pd.DataFrame object.'''

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline, make_pipeline

pd.options.mode.chained_assignment = None

def show_households(df):
    print
    print 'All households in this subset of data:'
    print df['LCLid'].unique()
    print
    print 'Total number of households: {}'.format(len(df['LCLid'].unique()))
    print
    return df['LCLid'].unique()

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

class DropIncompleteDays(object):

    def __init__(self):
        pass

    def transform(self, df):
        pass


if __name__ == '__main__':
    path_data = '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_1.csv'
    df = pd.read_csv(path_data)
    households = show_households(df)
    household = households[5]

    ch = ChooseHousehold(household)
    df = ch.transform(df)
    #
    csf = ConvertStrFloat('KWH/hh (per half hour) ')
    df = csf.transform(df)
    #
    ets = ExtractTimeSeries('DateTime', 'KWH/hh (per half hour) ')
    df = ets.transform(df)
    #
    print 'First and last 5 rows of time-series for the household_id: {}'.format(household)
    print df.head()
    print
    print df.tail()
