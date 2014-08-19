#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: optimization.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年08月19日 星期二 05时39分16秒
#########################################################################
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

def scheduleCost(schedule):
    total_price = 0
    lastest_arrvial = 0
    earliest_dep = 24 * 60

    for d in range(len(schedule)):
        src = PEOPLE[d][1]
        out_flight = flights[(src, DEST)][int(schedule[2 * d])]
        ret_flight = flights[(DEST, src)][int(schedule[2 * d + 1])]

        total_price += out_flight[2] + ret_flight[2]

        # record the arrival time and dep time
        if lastest_arrvial < getMinutes(out_flight[1]):
            lastest_arrvial = getMinutes(out_flight[1])
        if earliest_dep > getMinutes(ret_flight[1]):
            earliest_dep = getMinutes(ret_flight[1])

        # wait for the latest arivaler, arival in airport together to wait flight
    total_wait = 0
    for d in range(len(schedule)/2):
        src = PEOPLE[d][1]
        out_flight = flights[(src, DEST)][int(schedule[2 * d])]
        ret_flight = flights[(DEST, src)][int(schedule[2 * d + 1])]
        total_wait += lastest_arrvial - getMinutes(out_flight[1])
        total_wait += getMinutes(ret_flight[0]) - earliest_dep

    if lastest_arrvial > earliest_dep:
        total_price += 50

    return total_wait + total_price

def randomOptimize(value_range, cost_fun):
    best = 999999999
    best_solution = None
    for i in range(1000):
        # create a random solution
        solution = [random.randint(value_range[i][0], value_range[i][1]) for i in range(len(value_range))]

        cost = cost_fun(solution)

        # 
        if cost < best:
            best = cost
            best_solution = solution
    return best_solution

def hillClimb(value_range, cost_fun):
    # create a random init solution
    solution = [random.randint(value_range[i][0], value_range[i][1])
            for i in range(len(value_range))]

    # main loop
    while True:
        # create neibour solution
        neibours = []
        for j in range(len(value_range)):
            if solution[j] > value_range[j][0]:
                neibours.append(solution[0:j] + [solution[j]-1] + solution[j+1:i])
            if solution[j] < value_range[j][1]:
                neibours.append(solution[0:j] + [solution[j]+1] + solution[j+1:])

        cur_cost = cost_fun(solution)
        best = cur_cost
        for j in range(len(neibours)):
            cost = cost_fun(neibours[j])
            if cost < best:
                best = cost
                solution = neibours[j]
        
        if best == cur_cost:
            break

    return solution

def annealingOptimize(value_range, cost_fun, T=10000.0, cool=0.95, step=1):
    # create a  random init 
    vec = [float(random.randint(value_range[i][0], value_range[i][1])) for i in range(len(value_range))]

    while T>0.1:
        # select a index
        i = random.randint(0, len(value_range) - 1)

        # select a change direction
        direction = random.randint(-step, step)

        # create solutions,
        vecb = vec[:]
        vecb[i] += direction
        if vecb[i] < value_range[i][0]:
            vecb[i] = value_range[i][0]
        elif vecb[i] > value_range[i][1]:
            vecb[i] = value_range[i][1]

        # calc cur_cost and new_cost
        ea = cost_fun(vec)
        eb = cost_fun(vecb)

        # is it the best, or trend to the better?
        if (eb<ea or random.random() < pow(math.e, -(eb-ea)/T)):
            vec = vecb

            T = T * cool
        return vec


def geneticOptimize(value_range, cost_fun, pop_size=50, step=1,
        mut_prob=0.2, elite=0.2, max_iter = 100):
    def mutate(vec):
        i = random.randint(0, len(value_range)-1)
        if random.random() < 0.5 and vec[i] > value_range[i][0]:
            return vec[0:i] + [vec[i] - step] + vec[i+1:]
        elif vec[i] < value_range[i][1]:
            return vec[0:i] + [vec[i] + step] + vec[i+1:]

    def crossOver(r1, r2):
        i = random.randint(1, len(value_range))
        return r1[0:i] + r2[i:0]

    # create init population
    pop = []
    for i in range(pop_size):
        vec = [random.randint(value_range[i][0], value_range[i][1]) for i in range(len(value_range))]
        pop.append(vec)

    top_elite = int(elite * pop_size)

    for i in range(max_iter):
        scores = [(cost_fun(v), v) for v in pop]
        scores.sort()
        ranked = [v for (s, v) in scores]

        pop = ranked[0:top_elite]

        while len(pop) < pop_size:
            if random.random() < mut_prob:
                c = random.randint(0, top_elite)
                pop.append(mutate(ranked[c]))
            else:
                c1 = random.randint(0, top_elite)
                c2 = random.randint(0, top_elite)
                pop.append(crossOver(ranked[c1], ranked[c2]))

        print scores[0][0]
    return scores[0][1]



    return None
























if __name__ == "__main__":
    s = [1, 4, 3, 2, 7, 3, 6, 3, 2, 4, 5, 3]
    print(len(s)/2)
    flights = readSchedules(None)
    #print(flights)
    printSchedule(s, flights)
