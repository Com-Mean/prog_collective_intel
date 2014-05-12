#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: deliciousrec.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年05月09日 星期五 17时46分08秒
#########################################################################

from pydelicious import get_popular, get_userposts, get_urlposts
import time

def initializeUserDict(tag, count = 5):
    usr_dict = {}
    for most_popular in get_popular(tag = tag)[0 : count]:
        for person in get_urlposts(most_popular['href']):
            usr = person['user']
            usr_dict[usr] = {}
    return usr_dict


def fill_items(usr_dict):
    all_item = {}

    for usr in usr_dict:
        for i in range(3):
            try:
                posts = get_userposts(usr)
                break
            except Exception as e:
                print(str(e))
                time.sleep(4)
        for post in posts:
            url = post['href']
            usr_dict[usr][url] = 1.0
            all_item[url] = 1

    #if the url not in someone's post, then his ratings is 0.0,
    #make sure all datas have the same dimensionality
    for ratings in usr_dict.values():
        for item in all_item:
            if item not in ratings:
                ratings[item] = 0.0

if __name__ == "__main__":
    import random
    import prefer
    delc_usrs = initializeUserDict('Python')
    delc_usrs['lpq'] = {} #add yourself
    fill_items(delc_usrs)

    usr = delc_usrs.keys()[random.randint(0, len(delc_usrs) - 1)]
    prefer.topMatches(delc_usrs, usr)
