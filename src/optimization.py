""" This module solves optimization problem to send a signal to battery specifying
sequence of charge - discharge cycles and how much energy the battery should charge
or discharge at every time interval in the cycle."""
import pandas as pd
import numpy as np
from scipy.optimize import linprog

# Custom Modules:
from auxiliary_functions import plot_results, print_process, plot_battery_savings, extract_days

class MinimizeDailyBill(object):

    def __init__(self, battery_capacity, efficiency, charging_rate):
        self.C = battery_capacity
        self.e = efficiency
        self.alpha = charging_rate
        #
        self.daily_bill = None

    def fit(self, demand, price):
        p_vec = [-p[0] if i==2 else p[0] for j, p in enumerate(price.values) for i in xrange(3)]
        A_eq = [[1 if j==2 else 0 for j in xrange(len(p_vec))]] # This is initial condition a_0 = 0
        b_eq = [0]
        for i, s in enumerate(demand.values):
            # This is for constraint g_i = s_i
            A_eq.append([1 if j==3*i else 0 for j in xrange(len(p_vec))])
            b_eq.append(s[0])

        A_ub = []
        b_ub = []
        for i, s in enumerate(demand.values):
            # This loop is for constraint c_i <= alpha*C
            A_ub.append([1 if j==3*i+1 else 0 for j in xrange(len(p_vec))])
            b_ub.append(self.alpha*self.C)
            # This is for constraint a_i <= s_i same as a_i <= g_i
            A_ub.append([1 if j==3*i+2 else 0 for j in xrange(len(p_vec))])
            b_ub.append(s[0])
        #
        triplet = [0, -self.e, 1]
        for i in xrange(len(demand)):
            # This loop is for constraint sum(a_j) <= e*sum(c_j) j=0 to i
            row = []
            for j in xrange(i+1):
                row.extend(triplet)
            row.extend(np.zeros((len(p_vec) - 3*(i+1),), dtype=np.int))
            A_ub.append(row)
            b_ub.append(0)
        #
        triplet2 = [0, self.e, -1]
        for i in xrange(len(demand)):
            # This loop is for constraint -sum(a_j) <= e*[C - sum(c_j)] j=0 to i
            row = []
            for j in xrange(i+1):
                row.extend(triplet2)
            row.extend(np.zeros((len(p_vec) - 3*(i+1),), dtype=np.int))
            A_ub.append(row)
            b_ub.append(self.e*self.C)
        #
        res =\
        linprog(c=p_vec, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, options={"disp": False})
        self.daily_bill = res.fun
        #
        g = []
        c = []
        a = []
        E = []
        sum_c = 0
        sum_a = 0
        for i in xrange(len(demand)):
            g.append(res.x[3*i])
            c.append(res.x[3*i+1])
            a.append(res.x[3*i+2])
            #
            sum_c += c[i]
            sum_a += a[i]
            E.append(sum_c - sum_a/self.e)

        return pd.DataFrame(E, columns=['Battery'], index=demand.index)

def run_optimization(environment_params):
    household_id = environment_params['household_id'].values[0]
    model_name = environment_params['model_name'].values[0]
    part_of_week = environment_params['part_of_week'].values[0]
    train_days = str(environment_params['train_days'].values[0])
    #num_days_pred = int(environment_params['num_days_pred'].values[0])
    price_file_name = environment_params['price_file_name'].values[0]
    #
    path_to_pred = '../predictions/'+household_id+'_'+model_name+'_'+part_of_week+'_'+train_days+'.csv'
    path_to_test = '../predictions/'+household_id+'_test_'+part_of_week+'_'+train_days+'.csv'
    path_to_price = '../clean_data/'+price_file_name+'.csv'
    #
    print_process('Loading Predicted Demand, Test, and Pricing Data')
    demand = pd.read_csv(path_to_pred, parse_dates=True, index_col='Unnamed: 0')
    test = pd.read_csv(path_to_test, parse_dates=True, index_col='Unnamed: 0')
    test = pd.DataFrame(test.values, columns=[test.columns[0]], index=demand.index)
    price = pd.read_csv(path_to_price, parse_dates=True, index_col='Unnamed: 0')
    #
    ''' Extrapolation of one day pricing data to a number of days in the demand,
    in case there are no pricing data for the same number of days as in demand.'''
    demand_days = extract_days(demand)
    num_demand_days = len(demand_days)
    price_days = extract_days(price)
    num_price_days = len(price_days)
    if num_demand_days > num_price_days:
        price_last_day = price_days[num_price_days-1]
        price_dummy = price.query('index >= @price_last_day')
        for day_gap in xrange(num_demand_days-num_price_days):
            price = price.append(price_dummy)
    price = pd.DataFrame(price.values, columns=[price.columns[0]], index=demand.index)
    #
    battery_params = pd.read_csv('../params/battery_params.txt', delim_whitespace=True)
    battery_capacity_interval = battery_params['battery_capacity_interval'].values[0]
    battery_capacity_max =\
    battery_capacity_interval*(1+battery_params['battery_capacity_multiple'].values[0])
    efficiency = battery_params['efficiency'].values[0]
    charging_rate = battery_params['charging_rate'].values[0]
    #
    savings = []
    battery_capacities =\
    np.arange(battery_capacity_interval, battery_capacity_max, battery_capacity_interval)
    batteries = {}
    #
    for battery_capacity in battery_capacities:
        mdb = MinimizeDailyBill(battery_capacity, efficiency, charging_rate)
        battery = mdb.fit(demand, price)
        batteries[round(battery_capacity, 2)] = battery
        daily_bill_w_battery = mdb.daily_bill
        #
        ''' Computation of daily bill if there were no battery'''
        test_vec = np.array(test.values)
        price_vec = np.array(price.values)
        daily_bill_no_battery = np.dot(test_vec.T, price_vec)[0][0]
        saving = round(100.0*(daily_bill_no_battery-daily_bill_w_battery)/daily_bill_no_battery, 2)
        savings.append(saving)
        print '|==============================================================|'
        print 'Daily Bill with no Battery: {}'.format(daily_bill_no_battery)
        print
        print 'Daily Bill with Battery: {}'.format(daily_bill_w_battery)
        print
        print 'Daily Savings: {}% for the battery capacity: {}'.format(saving, round(battery_capacity, 2))
    #
    day_to_pred = demand.index[0].date()
    plot_battery_savings(battery_capacities, savings, day_to_pred, model_name, part_of_week, household_id, train_days)
    print
    battery_capacity = float(raw_input('Enter battery capacity for wich to plot battery phases of operation: '))
    plot_results(demand, price, batteries[battery_capacity], day_to_pred, model_name, part_of_week, household_id, train_days, battery_capacity)
