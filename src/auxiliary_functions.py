"""This module contains auxiliary functions"""
import matplotlib.pyplot as plt
import pandas as pd

def extract_days(df, datetime_col=None):
    '''INPUT: DataFrame of time series where index is datetime
       OUTPUT: list of unique days from DataFrame'''
    if datetime_col == None:
        datetimes = pd.to_datetime(df.index)
    else:
        datetimes = pd.to_datetime(df[datetime_col])
    days = []
    for i, datetime in enumerate(datetimes):
        if datetime.date() not in days:
            days.append(datetime.date())
    return days

def print_process(process):
    print
    print '## {}'.format(process)
    print

def plot_pred_test(df_test_day, df_pred, day_to_pred, model_name, environment_params):
    household_id = environment_params['household_id'].values[0]
    train_days = str(environment_params['train_days'].values[0])
    part_of_week = environment_params['part_of_week'].values[0]
    num_days_pred = str(environment_params['num_days_pred'].values[0])
    #
    plt.plot(df_test_day, color='b', label='Actual Demand')
    plt.plot(df_pred, color='g', label='Predicted Demand')
    plt.legend(loc='best', prop={'size':16})
    plt.xlabel('Time', fontsize=15)
    plt.ylabel(df_test_day.columns[0], fontsize=15)
    plt.title('Predicted and Actual Demand for {} days beginning at: {}'.format(num_days_pred,str(day_to_pred)), fontsize=15)
    plt.savefig('../img/'+household_id+'_'+model_name+'_'+part_of_week+'_'+train_days+'_'+num_days_pred+'.png')
    plt.show()

def plot_results(demand, price, battery, day_to_pred, model_name, part_of_week, household_id, train_days, battery_capacity):
    #used in optimization module
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    lns1 = ax1.plot(price, color='k', label=price.columns[0])
    #
    ax2 = ax1.twinx()
    lns2 = ax2.plot(battery, color='r', label='Battery')
    lns3 = ax2.plot(battery.index, [battery_capacity]*len(battery), 'r--', label='Battery Capacity')
    lns4 = ax2.plot(demand, color='g', label='Demand')
    #
    ax1.set_xlabel('Time', fontsize=15)
    ax1.set_ylabel(price.columns[0], fontsize=15)
    ax2.set_ylabel(demand.columns[0], fontsize=15)
    #
    lns = lns1+lns2+lns3+lns4
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc='best', prop={'size':9})
    #
    plt.title('Phases of the battery operation for: {}'.format(str(day_to_pred)), fontsize=15)
    plt.savefig('../img/'+household_id+'_'+model_name+'_'+part_of_week+'_'+train_days+'_'+'battery.png')
    plt.show()

def plot_battery_savings (battery_capacities, savings, day_to_pred, model_name, part_of_week, household_id, train_days):
    '''INPUT: list, list, string, string, string, string
        OUTPUT: None
        Saves figure with the plot of battery_capacities vs. savings.'''
    plt.plot(battery_capacities, savings, color='r')
    plt.grid(b=True, which='major', color='b', linestyle='--')
    plt.xlabel('Battery Capacity (kWh)', fontsize=15)
    plt.ylabel('Daily savings (%)', fontsize=15)
    plt.title('Savings as a function of battery capacity for: {}'.format(str(day_to_pred)), fontsize=15)
    plt.savefig('../img/'+household_id+'_'+model_name+'_'+part_of_week+'_'+train_days+'battery_savings.png')
    plt.show()
