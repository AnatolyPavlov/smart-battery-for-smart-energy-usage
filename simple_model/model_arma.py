


import pandas as pd
#import statsmodels.api as sm
import pyflux as pf
import cPickle as pickle
import matplotlib.pyplot as plt
from datetime import timedelta
from collections import defaultdict

# Custom Modules:
from auxiliary_functions import print_process

class EnsembleARMA(object):

    def __init__(self, household_id, p, q):
        self.household_id = household_id
        self.p = p
        self.q = q
        #
        self._models = dict()
        self.df_out = pd.DataFrame()

    def fit(self, df):
        '''The first step is to prepare data
        for multimodel training. Transform input
        time series into a set of time series for
        each hourly-slice in a day, where each time
        series for a given hour has days as its agument'''
        days = []
        for i, datetime in enumerate(df.index):
            if datetime.date() not in days:
                days.append(datetime.date())
        #
        day = days[0]
        nex_day = days[1]
        hours_in_day = []
        for i, datetime in enumerate(df.query('index >= @day and index < @nex_day').index):
            if datetime.time() not in hours_in_day:
                hours_in_day.append(datetime.time())
        #
        df['time'] = [d.time() for i, d in enumerate(df.index)]
        houry_sliced_data = {} # key=hour slice, values = pd.DataFrame with daily time series
        for hour in hours_in_day:
            houry_sliced_data[hour] = df[df['time']==hour].drop('time', axis=1)
        #
        '''Now data ready to be sent for training models for each hourly slice'''
        pred = []
        date = []
        time = []
        day_to_pred = df.index[-1].date() + timedelta(days=1)
        for hour in hours_in_day:
            model=\
            pf.ARIMA(data=houry_sliced_data[hour], ar=self.p, ma=self.q, target=df.columns[0])
            self._models[hour] = model.fit("MLE")
            #print '{} {} {}'.format(day_to_pred, hour, model.predict(h=1)[df.columns[0]][0])
            pred.append(model.predict(h=1)[df.columns[0]][0])
            date.append(str(day_to_pred))
            time.append(str(hour))
        self.df_out = pd.DataFrame({'date': date, 'time': time, df.columns[0]: pred})
        idx = pd.to_datetime(self.df_out['date'] + ' ' + self.df_out['time'])
        self.df_out = pd.DataFrame(self.df_out[df.columns[0]].values, columns=[df.columns[0]], index=idx)

    def predict(self, df):
        day_to_pred = df.index[0].date()
        nex_day = day_to_pred + timedelta(days=1)
        df_test_day = df.query('index >= @day_to_pred and index < @nex_day')
        #
        path_to_pred = \
        '../predictions/'+self.household_id+'_EnsembleARMA_'+str(day_to_pred)+'.csv'
        self.df_out.to_csv(path_to_pred)
        print '------------------------------------------------------------------------------'
        print 'Predictions saved into: {}'.format(path_to_pred)
        print
        print 'To run optimization for prediction of EnsembleARMA model type in command line:'
        print 'python simple_optimization.py {} <path_to_price>'.format(path_to_pred)
        #
        plt.plot(df_test_day)
        plt.plot(self.df_out)
        plt.title(str(day_to_pred))
        plt.show()
        return self.df_out

class PriceCorrARMA(object):

    def __init__(self, price_file_name, household_id, p, q):
        self.path_to_price = '../clean_data/'+price_file_name+'.csv'
        self.household_id = household_id
        self.p = p
        self.q = q
        #
        self._models = dict()
        self.df_out = pd.DataFrame()

    def fit(self, df):
        '''The first step is to prepare data
        for multimodel training.'''
        days = []
        for i, datetime in enumerate(df.index):
            if datetime.date() not in days:
                days.append(datetime.date())
        #
        day = days[0]
        nex_day = days[1]
        hours_in_day = []
        for i, datetime in enumerate(df.query('index >= @day and index < @nex_day').index):
            if datetime.time() not in hours_in_day:
                hours_in_day.append(datetime.time())
        #
        price = pd.read_csv(self.path_to_price, parse_dates=True, index_col='Unnamed: 0')
        prices_unique = price[price.columns[0]].unique()
        times_corr_by_price = defaultdict(list) # key=price, val=list of times for that price
        for i, pr in enumerate(price[price.columns[0]]):
            #print '{} {} {}'.format(i, pr, price.index[i].time())
            if pr in prices_unique:
                times_corr_by_price[pr].append(price.index[i].time())
        #print times_corr_by_price
        df['time'] = [d.time() for i, d in enumerate(df.index)]
        price_corr_data = {}
        for pr, times in times_corr_by_price.iteritems():
            price_corr_data[pr] =\
            {time: df[df['time']==time].drop('time', axis=1)[df.columns[0]].values for time in times}

        data_means_grouped_by_price = {}
        for pr, data in price_corr_data.iteritems():
            data_means_grouped_by_price[pr] = pd.DataFrame(pd.DataFrame(data).mean(axis=1).values,\
            columns=[df.columns[0]], index=days)
        #
        '''Now data ready to be sent for training models for each hourly slice'''
        dummy_pred = {}
        day_to_pred = df.index[-1].date() + timedelta(days=1)
        for pr in prices_unique:
            model=\
            pf.ARIMA(data=data_means_grouped_by_price[pr], ar=self.p, ma=self.q, target=df.columns[0])
            self._models[pr] = model.fit("MLE")
            dummy_pred[pr] = model.predict(h=1)[df.columns[0]][0]
        #
        date = []
        time_pred = []
        for pr in prices_unique:
            for time in times_corr_by_price[pr]:
                time_pred.append((time, dummy_pred[pr]))
                date.append(str(day_to_pred))
        #
        time, pred = zip(*sorted(time_pred, key=lambda tup: tup[0]))
        time = [str(t) for t in time]
        self.df_out = pd.DataFrame({'date': date, 'time': time, df.columns[0]: pred})
        idx = pd.to_datetime(self.df_out['date'] + ' ' + self.df_out['time'])
        self.df_out = pd.DataFrame(self.df_out[df.columns[0]].values, columns=[df.columns[0]], index=idx)
        self.df_out

    def predict(self, df):
        day_to_pred = df.index[0].date()
        nex_day = day_to_pred + timedelta(days=1)
        df_test_day = df.query('index >= @day_to_pred and index < @nex_day')
        #
        path_to_pred = \
        '../predictions/'+self.household_id+'_PriceCorrARMA_'+str(day_to_pred)+'.csv'
        self.df_out.to_csv(path_to_pred)
        print '------------------------------------------------------------------------------'
        print 'Predictions saved into: {}'.format(path_to_pred)
        print
        print 'To run optimization for prediction of PriceCorrARMA model type in command line:'
        print 'python simple_optimization.py {} {}'.format(path_to_pred, self.path_to_price)
        #
        plt.plot(df_test_day)
        plt.plot(self.df_out)
        plt.title(str(day_to_pred))
        plt.show()
        return self.df_out
