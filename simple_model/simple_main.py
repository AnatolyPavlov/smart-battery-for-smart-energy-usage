'''This is the main module which makes calls to functions in defferent
modules and runs them in order specified in this module. This module also
loads row data and outputs, if it is directed so, post-processed data and
it also saves the model in .pkl file.'''

import pandas as pd
import sys
from datetime import timedelta

# Custom Modules:
from simple_data_preprocessing import ChooseHousehold, ConvertStrFloat
from simple_data_preprocessing import CleanData, ExtractTimeSeries

def show_households(df):
    print
    print 'All households in this subset of data:'
    print df['LCLid'].unique()
    print
    print 'Total number of households: {}'.format(len(df['LCLid'].unique()))
    print
    return df['LCLid'].unique()

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


if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'data':
        path_data =\
        '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_1.csv'
        path_data2 =\
        '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_2.csv'
        print
        print '## Loading Data'
        print
        df = pd.read_csv(path_data)
        households = show_households(df)
        household = households[0]

        print
        print '## Data Preprocessing'
        print
        ch = ChooseHousehold(household)
        df = ch.transform(df)
        #
        csf = ConvertStrFloat('KWH/hh (per half hour) ')
        df = csf.transform(df)
        #
        cd = CleanData(datetime_col='DateTime', yt_col='KWH/hh (per half hour) ')
        df = cd.drop_duplicate_records(df)
        df = cd.drop_missing_val(df)
        df = cd.drop_null_val(df)
        df = cd.drop_incomplete_days(df)
        #
        ets = ExtractTimeSeries(datetime_col='DateTime', yt_col='KWH/hh (per half hour) ')
        df = ets.transform(df)
        #
        '''show_days_details(df)
        print
        print 'Above results are for the household_id: {}'.format(household)'''

        print
        print '## Saving Data'
        print
        df.to_csv('../clean_data/'+household+'.csv')

    if action == 'model':
        print
        print '## Training Model'
        print
