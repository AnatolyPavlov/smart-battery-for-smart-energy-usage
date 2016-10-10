'''This module contains arma model. It takes post-processed data provided via
simple_main.py module, splits these data into training and validating subsets,
trains model on training data and validates on validation data set. It saves
trained model as .pkl file, so that it can be uploaded and used to make predictions
and/or test the model on test data set.'''

import pandas as pd
import sys
import statsmodels.api as sm
from statsmodels.tsa.arima_process import arma_generate_sample

class TimeSeriesDataSplit(object):

    def __init__(self, train_set_final_date):
        self.train_set_final_date = train_set_final_date

    def train_test_split(self, df):
        pass


if __name__ == '__main__':
    path_to_clean_data = sys.argv[1]
    df = pd.read_csv(path_to_clean_data)
    tsds = TimeSeriesDataSplit()
    tsds.train_test_split(df)
