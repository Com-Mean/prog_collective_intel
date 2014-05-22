#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: search_engine.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年05月15日 星期四 10时54分52秒
#########################################################################
import urllib2
from BeautifulSoup import *
from urlparse import urljoin
import sqlite3 as sqlite


class crawler:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    def get_entry_id(self, table, field, value, createnew = True):
        return None

    def add_to_index(self, url, soup):
        print('Indexing %s'%url)

    def get_text_only(self, soup):
        return None

    def separate_words(self, text):
        return None

    def isindexed(self, url):
        return False

    def add_link_ref(self, url_from, url_to, link_text):
        pass

    def crawl(self, pages, depth=2):
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = urllib2.urlopen(page)
                except Exception as e:
                    print(str(e))
                    print("Could not open %s"%page)
                    continue
                soup = BeautifulSoup(c.read())
                self.add_to_index(page, soup)

                links = soup('a')
                for link in links:
                    if 'href' in dict(link.attrs):
                        url = urljoin(page, link['href'])
                        if url.find("'") is not -1: continue
                        url = url.split('#')[0] #delete position
                        if url[0:4] is 'http' and self.isindexed(url) is False:
                            newpages.add(url)
                        link_text = self.get_text_only(link)
                        self.add_link_ref(page, url, link_text)
                self.dbcommit()
            pages = newpages

    def create_index_tables(self):
        sql_cmds = (
                'create table urllist(url)',
                'create table wordlist(word)',
                'create table wordlocation(urlid, wordid, location)',
                'create table link(fromid integer, toid integer)',
                'create table linkwords(wordid, linkid)',
                'create index urlidx on urllist(url)',
                'create index wordidx on wordlist(word)',
                'create index wordurlidx on wordlocation(wordid)',
                'create index urltoidx on link(toid)',
                'create index urlfromidx on link(fromid)',)
        for cmd in sql_cmds:
            self.con.execute(cmd)
        self.dbcommit()

        pass

