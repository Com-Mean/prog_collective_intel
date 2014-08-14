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

#Layer relation
WORD_TO_HIDDEN = 0
HIDDEN_TO_URL  = 1

def dtanh(y):
    return 1.0 - y * y

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

    def generateHiddenNode(self, wordids, urls):
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
            print("hiddenid %d" % hiddenid)
            # set strength
            for wordid in wordids:
                self.setStrength(wordid, hiddenid, WORD_TO_HIDDEN, 1.0/len(wordids))
            for urlid in urls:
                self.setStrength(hiddenid, urlid, HIDDEN_TO_URL, 0.1)

    def getMatchedHiddenIds(self, wordids, urlids):
        ret = {}
        for wordid in wordids:
            word_toids = self.con.execute(
                    'select toid from wordhidden where fromid=%d' % wordid)
            for row in word_toids:
                ret[row[0]] = 1
        for urlid in urlids:
            url_fromids = self.con.execute(
                    'select fromid from hiddenurl where toid=%d' % urlid)
            for row in url_fromids:
                ret[row[0]] = 1
        return list(ret.keys())

    def setupNetwork(self, wordids, urlids):
        # value list
        self.wordids = wordids
        self.hiddenids = self.getMatchedHiddenIds(wordids, urlids)
        self.urlids = urlids

        #node output
        self.ai = [1.0] * len(self.wordids)
        self.ah = [1.0] * len(self.hiddenids)
        self.ao = [1.0] * len(self.urlids)

        #build the strength matrix
        self.wi = [[self.getStrength(wordid, hiddenid, 0)
                    for hiddenid in self.hiddenids]
                    for wordid in self.wordids]
        self.wo = [[self.getStrength(hiddenid, urlid, 1)
                    for urlid in self.urlids]
                    for hiddenid in self.hiddenids]

    def feedForward(self):
        # the wordids is the only input
        for i in range(len(self.wordids)):
            self.ai[i] = 1.0

        # hidden_layer's active level
        for j in range(len(self.hiddenids)):
            sum = 0.0
            for i in range(len(self.wordids)):
                sum = sum + self.ai[i] * self.wi[i][j]
            self.ah[j] = tanh(sum)

        # output_layer's active level
        for k in range(len(self.urlids)):
            sum = 0.0
            for j in range(len(self.hiddenids)):
                sum = sum + self.ah[j] * self.wo[j][k]
            self.ao[k] = tanh(sum)
        return self.ao[:]

    def getResult(self, wordids, urlids):
        self.setupNetwork(wordids, urlids)
        return self.feedForward()
    
    def backPropagate(self, targets, N=0.5):
        # calculate output layer deviation
        outputDeltas = [0.0] * len(self.urlids)
        for k in range(len(self.urlids)):
            error = targets[k] - self.ao[k]
            outputDeltas[k] = dtanh(self.ao[k]) * error

        #calculate hidden layer deviation
        hiddenDeltas = [0.0] * len(self.hiddenids)
        for j in range(len(self.hiddenids)):
            error = 0
            for k in range(len(self.urlids)):
                error = error + outputDeltas[k] * self.wo[j][k]
                hiddenDeltas[j] = dtanh(self.ah[j]) * error

        # output strength
        for j in range(len(self.hiddenids)):
            for k in range(len(self.urlids)):
                change = outputDeltas[k] * self.ah[j]
                self.wo[j][k] = self.wo[j][k] + N * change

        # input  strength
        for i in range(len(self.wordids)):
            for j in range(len(self.hiddenids)):
                change = hiddenDeltas[j] * self.ai[i]
                self.wi[i][j] = self.wi[i][j] + N * change

    def updateDatabase(self):
        # let the data in the database
        for i in range(len(self.wordids)):
            for j in range(len(self.hiddenids)):
                self.setStrength(self.wordids[i], self.hiddenids[j], WORD_TO_HIDDEN, self.wi[i][j])

            for k in range(len(self.urlids)):
                self.setStrength(self.hiddenids[j], self.urlids[k], HIDDEN_TO_URL, self.wo[j][k])

        self.con.commit()
                

    def trainQuery(self, wordids, urlids, selectedUrl):
        # create a hidden node if not exit
        self.generateHiddenNode(wordids, urlids)

        self.setupNetwork(wordids, urlids)
        self.feedForward()
        targets = [0.0] * len(urlids)
        targets[urlids.index(selectedUrl)] = 1.0

        self.backPropagate(targets)
        self.updateDatabase()
