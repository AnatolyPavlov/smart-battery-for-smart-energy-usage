'''This module is not a part of model nor data preprocessing. Its perpose is to
extract basic information about data and display it. This information will be
used to decide which household to chose to train the model and how many days
to use in order to train the model.'''

import pandas as pd
import sys
from datetime import timedelta

# Custom Modules:
from auxiliary_functions import print_process, extract_days
from data_preprocessing import ChooseHousehold, ExtractTimeSeries

def show_households(df):
    print
    print 'All households in this subset of data:'
    print df['LCLid'].unique()
    print
    print 'Total number of households: {}'.format(len(df['LCLid'].unique()))
    print
    return df['LCLid'].unique()


def show_households_details(df, household_id, datetime_col):
    ets = ExtractTimeSeries(datetime_col, 'KWH/hh (per half hour) ')
    df = ets.transform(df)
    days = extract_days(df)
    #
    temp = pd.DatetimeIndex(df.index)
    df['weekday'] = temp.weekday
    df_weekdays = df[df['weekday'] <= 4]
    weekdays = extract_days(df_weekdays)
    df_weekends = df[df['weekday'] > 4]
    weekends = extract_days(df_weekends)
    print
    print 'The total number of days for the household {} is: {}, where weekdays: {} and weekends: {}'\
    .format(household_id,len(days),len(weekdays),len(weekends))
    print

def main():
    file_num = raw_input('Enter the file number (1 to 168) which you want to look at: ')
    path_to_data = '../data/Power-Networks-LCL-June2015(withAcornGps)v2_'+file_num+'.csv'

    print_process('Loading Data')
    df = pd.read_csv(path_to_data)
    #
    households = show_households(df)
    for household_id in households:
        ch = ChooseHousehold(household_id)
        dfh = ch.transform(df)
        show_households_details(dfh, household_id, 'DateTime')


if __name__ == '__main__':
    main()
