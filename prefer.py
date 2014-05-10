#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: prefer.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年05月05日 星期一 12时43分29秒
#########################################################################

import os, math

movies =('Lady in the Water', 'Snake on a Plane','Just My Luck', 'Superman Returns', 'You, Me and Dupree', 'The Night Listener')
critics = {}

def keys_values_map(keys, values, defval = None):
    tmp={}.fromkeys(keys, defval)
    for idx in range(len(values)):
        tmp[keys[idx]] =  values[idx]

    return tmp

def creat_critics_data(critic_dict):
    critic_dict['Lisa Rose'] = keys_values_map(movies, (2.5, 3.5, 3.0, 3.5, 2.5, 3.0))
    critic_dict['Gene Seymour'] = keys_values_map(movies, (3.0, 3.5, 1.5, 5.0, 3.5, 3.0))
    critic_dict['Michael Philips'] = keys_values_map(movies, (2.5, 3.0, 3.5, 0.0, 0.0, 4.0))
    critic_dict['Claudia Puig'] = keys_values_map(movies, (0.0, 3.5, 3.0, 4.0, 2.5, 4.5))
    critic_dict['Mick LaSalle'] = keys_values_map(movies, (3.0, 4.0, 2.0, 3.0, 2.0, 3.0))
    critic_dict['Jack Matthews'] = keys_values_map(movies, (3.0, 4.0, 3.0, 5.0, 3.5, 0.0))
    critic_dict['Toby'] = {movies[1]:4.5, movies[3]:4.0, movies[4]:1.0}
    return critic_dict

def get_same_items(maps, key1, key2):
    si = {}
    for item in maps[key1]:
        if item in maps[key2]:
            si[item] = 1
    return si

# key value reverse
def transform_prefers(prefers):
    result = {}
    for item in prefers:
        for it in prefers[item]:
            result.setdefault(item, {})
            result[it][item] = prefers[item][it]
    return result


def euclidean_distance(maps, key1, key2):
    si = get_same_items(maps, key1, key2)
    #no same thing
    if 0 == len(si): return 0

    sum_of_squares = sum([pow(maps[key1][item] - maps[key2][item], 2) for item in si])
    return 1/(1 + math.sqrt(sum_of_squares))

def tanimoto_score(maps, key1, key2):
    if 0 == len(maps[key1]) and 0 == len(maps[key2]):
        return 1
    same_items = get_same_items(maps, key1, key2)
    return len(same_items) / (len(maps[key1]) + len(maps[key2]) - len(same_items))


def pearson_correlation_score(maps, key1, key2):
    si = get_same_items(maps, key1, key2)
    si_len = len(si)
    #no same thing
    if 0 == si_len: return 1

    sum1 = sum([maps[key1][it] for it in si])
    sum2 = sum([maps[key2][it] for it in si])

    sum1sq = sum([pow(maps[key1][it], 2) for it in si])
    sum2sq = sum([pow(maps[key2][it], 2) for it in si])
    psum = sum([maps[key1][it] * maps[key2][it] for it in si])

    #calculate pcs
    num = psum - (sum1*sum2/si_len)
    den = math.sqrt((sum1sq - pow(sum1, 2)/si_len) * (sum2sq - pow(sum2, 2)/si_len))

    if den == 0: return 0
    return num/den

def top_matches(maps, person, n=5, similarity = pearson_correlation_score):
    scores = [(similarity(maps, person, other), other) \
            for other in maps if other != person]
    #
    scores.sort()
    scores.reverse()
    return scores[0:n]

def get_recommendations(maps, person, similarity=euclidean_distance):
    totals = {}
    sim_sums = {}
    person_keys = maps[person].keys()
    for other in maps:
        if other == person: continue
        sim = similarity(maps, person, other)

        if sim <= 0: continue
        for item in maps[other]:
            if item not in person_keys or 0.0 == maps[person][item]:
                totals.setdefault(item, 0)
                totals[item]+=maps[other][item] * sim
                sim_sums.setdefault(item, 0)
                sim_sums[item] += sim

    rankings = [(total/sim_sums[item], item) for item, total in totals.items()]

    rankings.sort()
    rankings.reverse()
    return rankings

def calculate_similar_items(prefers, n = 10):
    c = 0
    result = {}
    item_prefers = transform_prefers(prefers)

    for item in item_prefers:
        c += 1

        if c % 100 == 0: print('%d / %d'%(c, len(item_prefers)))
        scores = top_matches(item_prefers, item, n = n, similarity = euclidean_distance)
        result[item] = scores
    return result

def get_recommended_items(perfers, item_match, usr):
    usr_ratings = perfers[usr]
    scores = {}
    total_sim = {}

    for (item, rating) in usr_ratings.items():
        for (sim, item2) in item_match[item]:
            if item2 in usr_ratings: continue
            scores.setdefault(item2, 0)
            scores[item2] += sim

    #计算加权平均值
    rankings = [(score / total_sim[item], item) for item, score in scores.items()]
    rankings.sort()
    rankings.reverse()
    return rankings

# data from http://grouplens.org/datasets/movielens/
def load_movies_lens(path='/data/movielens'):
    movies = {}
    for line in open(path + '/u.item'):
        (id, title) = line.split('|')[0:2]
        movies[id] = title

    prefers = {}
    for line in open(path + '/u.data'):
        (usr, movieid, rating, time) = line.split('\t')
        prefers[usr][movies[movieid]] = float(rating)

    return prefers

