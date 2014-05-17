#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: searchengine.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年05月18日 星期日 05时23分32秒
#########################################################################

import urllib2
from BeautifulSoup import *
from urlparse import urljoin
import sqlite3 as sqlite

Ignore_words = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])
class Crawler:
    def __init__(self, dbname):
        pass

    def crawl(self, pages, depth=2):
        pass

    def get_text_only(self, soup):
        pass

class Searcher:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def get_scored_list(self, rows, word_ids):
        total_scores = dict([(row[0], 0) for row in rows])

        #TODO evaluate function
        weights = []
        for (weight, scores) in weights:
            for url in total_scores.keys():
                total_scores[url] += weight * scores[url]
        
        return total_scores

    def get_url_name(self, id):
        return self.con.execute(
                "select url from urllist where rowid=%d"%id).fetchone()[0]

    def query(self, q):
        rows, word_ids = self.get_match_rows(q)
        scores = self.get_scored_list(rows, word_ids)

        ranked_scores = sorted([(score, url) for (url, score) in scores.items()], \
                reverse = True)
        for (score, url_id) in ranked_scores[0:10]:
            print('%f\t%s'%(score, self.get_url_name(url_id)))


    def get_match_rows(self, q):
        field_list = 'w0.rulid'
        table_list = ''
        clause_list = ''
        word_ids = []

        words = q.split(' ')
        table_num = 0

        if word in words:
            word_row = self.con.execute(
                    "select rowid from wordlist where word='%s'"%word).fetchone()
