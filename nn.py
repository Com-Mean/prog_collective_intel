#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: nn.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年08月13日 星期三 05时56分24秒
#########################################################################
from math import tanh
import sqlite3 as sqlite


DEFAULT_STRENGTH_WORD_TO_HIDDEN = -0.2
DEFAULT_STRENGTH_HIDDEN_TO_URL  = 0
LAYER_KEY = ('WORD_TO_HIDDEN', 'HIDDEN_TO_URL')
LAYER = { LAYER_KEY[0]: 0,
          LAYER_KEY[1]: 1,}


class SearchNet:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def createTables(self):
        self.con.execute('create table hiddennode(create_key)')
        self.con.execute('create table wordhidden(fromid, toid, strength)')
        self.con.execute('create table hiddenurl(fromid, toid, strength)')
        self.con.commit()

    def getStrength(self, fromid, toid, layer):
        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'

        strength = self.con.execute('select strength from %s where fromid = %d and toid=%d' % (table, fromid, toid)).fetchone()

        if strength == None:
            if layer == 0: return DEFAULT_STRENGTH_WORD_TO_HIDDEN
            if layer == 1: return DEFAULT_STRENGTH_HIDDEN_TO_URL
        return strength[0]

    def setStrength(self, fromid, toid, layer, strength):
        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'

        cur_strength = self.con.execute('select rowid from %s where fromid=%d and toid=%d' % (table, fromid, toid)).fetchone()
        if cur_strength == None:
            self.con.execute('insert into %s(fromid, toid, strength) values(%d, %d, %f)' % (table, fromid, toid, strength))
        else:
            rowid = cur_strength[0]
            self.con.execute('update %s set strength=%f where rowid=%d' % (table, strength, rowid))

    def generatorHiddenNode(self, wordids, urls):
        if len(wordids) > 3:
            return None

        #check if the node is exist
        createkey = '_'.join(sorted([str(wordid) for wordid in wordids]))
        cur_row = self.con.execute(
                "select rowid from hiddennode where create_key='%s'" % createkey).fetchone()

        # insert if none
        if cur_row == None:
            new_row = self.con.execute(
                    "insert into hiddennode (create_key) values ('%s')" %createkey)
            hiddenid = new_row.lastrowid
            # set strength
            for wordid in wordids:
                self.setStrength(wordid, hiddenid, LAYER["WORD_TO_HIDDEN"], 1.0/len(wordid))
            for urlid in urls:
                self.setStrength(hiddenid, urlid, LAYER["HIDDEN_TO_URL"], 0.1)

