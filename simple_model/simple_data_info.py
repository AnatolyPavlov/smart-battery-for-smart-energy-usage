'''This module is not a part of model nor data preprocessing. Its perpose is to
extract basic information about data and display it. This information will be
used to decide which household to chose to train model for and which dates to
chose to split time series data into training, validation and test subsets.'''

import pandas as pd
import sys
from datetime import timedelta

# Custom Modules:
from simple_data_preprocessing import ChooseHousehold

def show_households(df):
    print
    print 'All households in this subset of data:'
    print df['LCLid'].unique()
    print
    print 'Total number of households: {}'.format(len(df['LCLid'].unique()))
    print
    return df['LCLid'].unique()


def show_days_details(df, datetime_col):#, day_index=0):
    datetimes = pd.to_datetime(df[datetime_col])
    days = []
    for i, datetime in enumerate(datetimes):
        if datetime.date() not in days:
            days.append(datetime.date())

    print 'Printing all days for this household:'
    print
    for i, day in enumerate(days):
        next_day = day + timedelta(days=1)
        df_day = df[(datetimes >= day) & (datetimes < next_day)]
        print '{}, {}, {}'.format(i, day, len(df_day))
    print
    print 'Total number of days for this household: {}'.format(len(days))
    print

    # show a single day time-series
    '''day = days[day_index]
    next_day = day + timedelta(days=1)
    df_day = df.query('index >= @day and index < @next_day')
    print
    print 'Time-series for {}. Todal number of records: {}'.format(day, len(df_day))
    print
    print df_day'''

def main():
    path_data =\
    '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_1.csv'
    path_data2 =\
    '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_2.csv'
    print
    print '## Loading Data'
    print
    df = pd.read_csv(path_data)
    #
    households = show_households(df)
    household = households[0]
    ch = ChooseHousehold(household)
    df = ch.transform(df)
    #
    print 'Details of the household: {}'.format(household)
    print
    show_days_details(df, 'DateTime')


if __name__ == '__main__':
    main()
