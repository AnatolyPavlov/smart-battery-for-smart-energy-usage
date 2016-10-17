"""This module contains auxiliary functions"""
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


def print_process(process):
    print
    print '## {}'.format(process)
    print

def plot_pred_test(df_test_day, df_pred, day_to_pred, model_name):
    plt.plot(df_test_day, color='b', label='Actual Demand')
    plt.plot(df_pred, color='g', label='Predicted Demand')
    plt.legend(loc='best')
    plt.xlabel('Time')
    plt.ylabel(df_test_day.columns[0])
    plt.title('Predicted-(model: {}) and Actual Demand for the following day: {}'.format(model_name, str(day_to_pred)))
    plt.show()

def plot_results(demand, price, battery, day_to_pred):
    #used in optimization module
    plt.plot(price, color='k', label='Pricing')
    plt.plot(demand, color='g', label='Demand')
    plt.plot(battery, color='r', label='Battery')
    plt.legend(loc='best')
    plt.ylabel(demand.columns[0])
    plt.xlabel('Time')
    plt.title('''Daily ({}) phases of stand by, charge, and discharge cycles of the battery.'''.format(day_to_pred))
    plt.show()
