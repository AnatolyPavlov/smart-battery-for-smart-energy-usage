'''This module is not a part of model nor data preprocessing. Its perpose is to
extract basic information about data and display it. This information will be
used to decide which household to chose to train the model and how many days
to use in order to train the model.'''

import pandas as pd
import sys
from datetime import timedelta

# Custom Modules:
from auxiliary_functions import print_process
from data_preprocessing import ChooseHousehold

def show_households(df):
    print
    print 'All households in this subset of data:'
    print df['LCLid'].unique()
    print
    print 'Total number of households: {}'.format(len(df['LCLid'].unique()))
    print
    return df['LCLid'].unique()


def show_households_details(df, household_id, datetime_col):
    datetimes = pd.to_datetime(df[datetime_col])
    days = []
    for i, datetime in enumerate(datetimes):
        if datetime.date() not in days:
            days.append(datetime.date())

    print
    print 'Total number of days for the household {} is: {}'.format(household_id, len(days))
    print

def main():
    path_data =\
    '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_1.csv'
    path_data2 =\
    '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_2.csv'

    print_process('Loading Data')
    df = pd.read_csv(path_data)
    #
    households = show_households(df)
    for household_id in households:
        ch = ChooseHousehold(household_id)
        df = ch.transform(df)
        show_households_details(df, household_id, 'DateTime')


if __name__ == '__main__':
    main()
