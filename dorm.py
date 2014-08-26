#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: dorm.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年08月19日 星期二 21时19分24秒
#########################################################################

import random
import math

# dormination, a room be lived by tow people
dorms = ['Zeus', 'Athena', 'Hercules', 'Bacchus', 'Pluto']

# stutdents' prefer dorm
perfers = [('Tony', ('Bacchus', 'Hercules')),
           ('Steve', ('Zeus', 'Pluto')),
           ('Andrea', ('Athena', 'Zeus')),
           ('Sarah', ('Zeus', 'Pluto')),
           ('Dave', ('Athena', 'Bacchus')),
           ('Jeff', ('Hercules', 'Pluto')),
           ('Fred', ('Pluto', 'Athena')),
           ('Suzie', ('Bacchus', 'Hercules')),
           ('Laura', ('Bacchus', 'Hercules')),
           ('Neil', ('Hercules', 'Athena')),]

# [(0,9), (0,8), (0,7), (0,6), (0,5), (0,4), (0,3), (0,2), (0,1), (0,0)]
domain = [(0, (len(dorms) * 2) - 1 - i) for i in range(0, len(dorms) * 2)]

def printSolution(vec):
    slots = []
    # tow slot a dorm
    for i in range(len(dorms)):
        slots += [i, i]
    for i in range(len(vec)):
        x = int(vec[i])

        # select from remain slots
        dorm = dorms[slots[x]]
        # print students and the dorm
        print(perfers[i][0], dorm)
        del slots[x]

def dormCost(vec):
    cost = 0
    #create a slots
    slots = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]

    # traverse everyone student
    for i in range(len(vec)):
        x = int(vec[i])
        dorm = dorms[slots[x]]
        perfer_dorm = perfers[i][1]
        if perfer_dorm[0] == dorm:
            cost += 0
        elif perfer_dorm[1] == dorm:
            cost += 1
        else:
            cost += 3

        del slots[x]
    return cost
