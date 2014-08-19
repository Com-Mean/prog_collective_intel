#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: optimization.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年08月19日 星期二 05时39分16秒
#########################################################################
import os
import time
import random
import math

PEOPLE = [('Seymour', 'BOS'),
          ('Franny',  'DAL'),
          ('Zooey',   'CAK'),
          ('Walt',    'MIA'),
          ('Buddy',   'ORD'),
          ('Les',     'OMA')]

DEST = 'LGA'


def readSchedules(filename):
    flights = {}
    for line in open('schedule.txt'):
        src, dest, depart, arrive, price = line.strip().split(',')
        flights.setdefault((src, dest), [])
        flights[(src, dest)].append((depart, arrive, int(price)))

    return flights

def getMinutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]

def printSchedule(r, flights):
    for d in range(int(len(r)/2)):
        name = PEOPLE[d][0]
        src = PEOPLE[d][1]
        out = flights[(src, DEST)][r[2 * d]]
        ret = flights[(DEST, src)][r[2 * d + 1]]
        print('%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % 
                (name, src, 
                 out[0], out[1], out[2],
                 ret[0], ret[1], ret[2]))

if __name__ == "__main__":
    s = [1, 4, 3, 2, 7, 3, 6, 3, 2, 4, 5, 3]
    print(len(s)/2)
    flights = readSchedules(None)
    #print(flights)
    printSchedule(s, flights)
