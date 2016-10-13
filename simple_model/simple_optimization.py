""" This module solves optimization problem to give a signal to battery specifying
sequence of chage - discharge cycles and how much energy battery should charge
or discharge at every step in the cycle.

To run this module type in command line:
python simple_optimization.py <path_to_demand> <path_to_price>"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

class MinimizeBill(object):

    def __init__(self, battery_capacity, efficiency, charging_rate):
        self.battery_capacity = battery_capacity
        self.efficiency = efficiency
        self.charging_rate = charging_rate
        #
        self.g = list()
        self.c = list()
        self.a = list()

    def fit(self, demand, price):
        p_vec = [-p[0] if i==2 else p[0] for j, p in enumerate(price.values) for i in xrange(3)]
        A_eq = []
        b_eq = []
        for i, s in enumerate(demand.values):
            A_eq.append([1 if j in [3*i,3*i+2] else 0 for j in xrange(len(p_vec))])
            b_eq.append(s[0])
        #
        res = linprog(c=p_vec, A_eq=A_eq, b_eq=b_eq, options={"disp": True})
        for i in xrange(len(demand)):
            self.g.append(res.x[3*i])
            self.c.append(res.x[3*i+1])
            self.a.append(res.x[3*i+2])
        '''print 'g:', self.g
        print
        print 'c:', self.c
        print
        print 'a:', self.a'''
        return pd.DataFrame(self.a, columns=['Battery Discharge (kWh in half hour)'], index=demand.index)


def plot(demand, price, battery):
    plt.plot(demand, color='g', label='Demand')
    plt.plot(price, color='k', label='Pricing')
    plt.plot(battery, color='r', label='Battery')
    plt.legend(loc='best')
    plt.xlabel('Time')
    plt.show()

def main():
    path_to_demand = sys.argv[1]
    path_to_price = sys.argv[2]
    print
    print '## Loading Demand and Pricing Data'
    print
    demand = pd.read_csv(path_to_demand, parse_dates=True, index_col='Unnamed: 0')
    demand = demand[:'2012-12-14 23:30:00']
    price = pd.read_csv(path_to_price, parse_dates=True, index_col='Unnamed: 0')
    price = pd.DataFrame(price.values, columns=[price.columns[0]], index=demand.index)
    #plot(demand, price)
    #
    mb = MinimizeBill(battery_capacity=10, efficiency=0.8, charging_rate=0.25)
    battery = mb.fit(demand, price)
    plot(demand, price, battery)

if __name__ == '__main__':
    main()
