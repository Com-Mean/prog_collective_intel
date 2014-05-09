#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: deliciousrec.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年05月09日 星期五 17时46分08秒
#########################################################################

from pydelicious import get_popular, get_userposts, get_urlposts

def initializeUserDict(tag, count = 5):
    usr_dict = {}
    for most_popular in get_popular(tag = tag)[0 : count]:
        for person in get_urlposts(most_popular['href']):
            usr = person['user']
            usr_dict[usr] = {}
    return usr_dict

