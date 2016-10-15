"""This module contains auxiliary functions"""
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


def print_process(process):
    print
    print '## {}'.format(process)
    print

def plot_acf_pacf(df, lags):
   fig = plt.figure(figsize=(12,8))
   ax1 = fig.add_subplot(211)
   fig = plot_acf(df, lags=lags, ax=ax1)
   ax2 = fig.add_subplot(212)
   fig = plot_pacf(df, lags=lags, ax=ax2)
   plt.show()
