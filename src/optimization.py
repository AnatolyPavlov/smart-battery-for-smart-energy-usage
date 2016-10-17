""" This module solves optimization problem to send a signal to battery specifying
sequence of charge - discharge cycles and how much energy the battery should charge
or discharge at every time interval in the cycle.

To run this module type in command line:
python optimization.py <path_to_demand> <path_to_price>"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

# Custom Modules:
from auxiliary_functions import plot_results, print_process

class MinimizeDailyBill(object):

    def __init__(self, battery_capacity, efficiency, charging_rate):
        self.C = battery_capacity
        self.e = efficiency
        self.alpha = charging_rate
        #
        self.g = list()
        self.c = list()
        self.a = list()
        self.E = list()
        #
        self.daily_bill = None

    def fit(self, demand, price):
        p_vec = [-p[0] if i==2 else p[0] for j, p in enumerate(price.values) for i in xrange(3)]
        A_eq = []
        b_eq = []
        for i, s in enumerate(demand.values):
            # This loop is for constraint s_i = g_i + a_i
            A_eq.append([1 if j in [3*i, 3*i+2] else 0 for j in xrange(len(p_vec))])
            b_eq.append(s[0])

        A_ub = []
        b_ub = []
        for i in xrange(len(demand)):
            # This loop is for constraint c_i <= alpha*C
            A_ub.append([1 if j==3*i+1 else 0 for j in xrange(len(p_vec))])
            b_ub.append(self.alpha*self.C)
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
        res = linprog(c=p_vec, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, options={"disp": False})
        self.daily_bill = res.fun
        sum_c = 0
        sum_a = 0
        for i in xrange(len(demand)):
            self.g.append(res.x[3*i])
            self.c.append(res.x[3*i+1])
            self.a.append(res.x[3*i+2])
            #
            sum_c += self.c[i]
            sum_a += self.a[i]
            self.E.append(sum_c - sum_a/self.e)

        return pd.DataFrame(self.E, columns=['Battery Charge Level'], index=demand.index)

def run_optimization(path_to_demand, path_to_test, path_to_price):
    print_process('Loading Demand, Test, and Pricing Data')
    demand = pd.read_csv(path_to_demand, parse_dates=True, index_col='Unnamed: 0')
    test = pd.read_csv(path_to_test, parse_dates=True, index_col='Unnamed: 0')
    test = pd.DataFrame(test.values, columns=[test.columns[0]], index=demand.index)
    price = pd.read_csv(path_to_price, parse_dates=True, index_col='Unnamed: 0')
    price = pd.DataFrame(price.values, columns=[price.columns[0]], index=demand.index)
    #
    mdb = MinimizeDailyBill(battery_capacity=0.5, efficiency=0.8, charging_rate=0.25)
    battery = mdb.fit(demand, price)
    daily_bill_w_battery = mdb.daily_bill
    #
    ''' Computation of daily bill if there were no battery'''
    test_vec = np.array(test.values)
    price_vec = np.array(price.values)
    daily_bill_no_battery = np.dot(test_vec.T, price_vec)[0][0]
    save_per = round(100.0*(daily_bill_no_battery-daily_bill_w_battery)/daily_bill_no_battery, 1)
    print
    print 'Daily Bill with no Battery: {} (UK Pounds)'.format(daily_bill_no_battery)
    print
    print 'Daily Bill with Battery: {} (UK Pounds)'.format(daily_bill_w_battery)
    print
    print 'Savings: {}%'.format(save_per)
    #
    day_to_pred = demand.index[0].date()
    plot_results(demand, price, battery, day_to_pred)


def main():
    path_to_demand = sys.argv[1]
    path_to_price = sys.argv[2]
    print_process('Loading Demand and Pricing Data')
    demand = pd.read_csv(path_to_demand, parse_dates=True, index_col='Unnamed: 0')
    price = pd.read_csv(path_to_price, parse_dates=True, index_col='Unnamed: 0')
    price = pd.DataFrame(price.values, columns=[price.columns[0]], index=demand.index)
    #
    mdb = MinimizeDailyBill(battery_capacity=0.5, efficiency=0.8, charging_rate=0.25)
    battery = mdb.fit(demand, price)
    plot_results(demand, price, battery)

if __name__ == '__main__':
    main()
