""" This script reads and transforms pricing data to pd.DataFrame as time-series"""

import pandas as pd
from datetime import timedelta

# Custom Modules:
from data_preprocessing import ExtractTimeSeries
from auxiliary_functions import print_process

def main():
    df = pd.read_excel('../data/Tariffs.xlsx')
    df.loc[df['Tariff'] == 'Low', 'Tariff'] = 0.0399
    df.loc[df['Tariff'] == 'Normal', 'Tariff'] = 0.1176
    df.loc[df['Tariff'] == 'High', 'Tariff'] = 0.6720
    #
    ets = ExtractTimeSeries(datetime_col='TariffDateTime', yt_col='Tariff')
    df = ets.transform(df)
    #
    day = pd.to_datetime('2013-12-27').date()
    next_day = day + timedelta(days=1)
    df_out = df.query('index >= @day and index < @next_day')
    df_out.columns=['Tariff (UK Pounds)']
    #
    print_process('Saving Post-Processed Data')
    path_to_price = '../clean_data/price_data_London.csv'
    df_out.to_csv(path_to_price)
    print 'Tariff data saved into: {}'.format(path_to_price)
    print

if __name__ == '__main__':
    main()
