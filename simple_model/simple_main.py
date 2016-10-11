'''This is the main module which makes calls to functions in defferent
modules and runs them in order specified in this module. This module also
loads row data and outputs, if it is directed so, post-processed data and
it also saves the model in .pkl file.'''

''' To run this module, type in command line the following depending on
what do you want to do:

To run data preprocessing: python simple_main.py data household_id

To train model: python simple_main.py model path_to_clean_data
'''

import pandas as pd
import sys
from datetime import timedelta

# Custom Modules:
from simple_data_preprocessing import ChooseHousehold, ConvertStrFloat,\
CleanData, ExtractTimeSeries


if __name__ == '__main__':
    action = sys.argv[1]
    household_id = sys.argv[2]
    if action == 'data':
        path_data =\
        '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_1.csv'
        path_data2 =\
        '../data/Power-Networks-LCL-June2015(withAcornGps).csv_Pieces/Power-Networks-LCL-June2015(withAcornGps)v2_2.csv'
        print
        print '## Loading Data'
        print
        df = pd.read_csv(path_data)

        print
        print '## Data Preprocessing'
        print
        ch = ChooseHousehold(household_id)
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
        print
        print '## Saving Data'
        print
        path_to_clean_data = '../clean_data/'+household_id+'.csv'
        df.to_csv(path_to_clean_data)
        print 'Clean data saved in: {}'.format(path_to_clean_data)
        print
        print 'To train model type in command line:'
        print 'python simple_main.py model {}'.format(path_to_clean_data)
        print

    if action == 'model':
        print
        print '## Training Model'
        print
        path_to_clean_data = sys.argv[2]
        df = pd.read_csv(path_to_clean_data)
        print df.head()
