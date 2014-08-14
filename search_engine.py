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
import nn
mynet = nn.SearchNet("nn.db")

PAGERANK_INIT_VALUE = 0.15
PAGERANK_DAMPING_RATIO = 0.85
Ignore_words = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])
class crawler:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    def get_entry_id(self, table, field, value, createnew = True):
        cur = self.con.execute(
                "select rowid from %s where %s='%s'" % (table, field, value))
        res = self.fetchone()
        if res == None:
            cur = self.con.execute(
                    " insert into %s (%s) values ('%s')" % (table, field, value))
            return cur.lastrowid
        else:
            return res[0]

    def add_to_index(self, url, soup):
        if self.isindexed(url): return
        print('Indexing %s'%url)

        #get a word
        text = self.get_text_only(soup)
        words = self.separate_words(text)

        #get the urlid
        urlid = self.get_entry_id('urllist', 'url', url)

        #get the link between words and the url
        for i in range(len(words)):
            word = words[i]
            if word in Ignore_words: continue
            wordid = self.get_entry_id('wordlist', 'word', word)
            self.con.execute("insert into wordlocation(urlid, wordid, location) values (%d, %d, %d)" % (urlid, wordid, i))


    def get_text_only(self, soup):
        v = soup.string
        if v == None:
            c = soup.contents
            result_text = ''
            for t in c:
                subtext = self.get_text_only(t)
                result_text += subtext + '\n'
            return result_text
        else:
            return v.strip()

    def separate_words(self, text):
        splitter = re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s != '']

    def isindexed(self, url):
        u = self.con.execute(
                "select rowid from urllist where url='%s'" %url).fetchone()
        if u != None:
            v = self.con.execute(
                    "select * from wordlocation where urlid=%d" % u[0]).fetchone()
            if v != None: return True
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

                #get the link in this page for next craw
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

    def calculatePageRank(self, iterrations = 20):
        # clear the pageRank table
        self.con.execute('drop table if exists pagerank')
        self.con.execute('create table pagerank(urlid primary key, score)')

        #give a init value 
        self.con.execute('insert into pagerank select rowid, 1.0 from urllist')
        self.dbcommit()

        for it in range(iterrations):
            print "Iteration %d" % (it)
            for (urlid,) in self.con.execute('select rowid from urllist'):
                pr = PAGERANK_INIT_VALUE

                # search the links which link to this link 
                for (from_linker,) in self.con.execute(
                        'select distinct fromid from link where toid=%d' % urlid):
                    from_linker_pr = self.con.execute(
                            'select score from pagerank where urlid=%d' % from_linker).fetchone()[0]

                    from_linker_toid_count = self.con.execute(
                            'select count(*) from link where fromid=%d' % from_linker).fetchone()[0]
                    pr += PAGERANK_DAMPING_RATIO * (from_linker_pr / from_linker_toid_count)
                    self.con.execute(
                        'update pagerank set score=%f where urlid=%d' % (pr, urlid))
                self.dbcommit()




#pp.87
class Searcher:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def get_scored_list(self, rows, word_ids):
        total_scores = dict([(row[0], 0) for row in rows])

        #evaluate function
        weights = [(1.0, self.frequencyScore(rows)),
                   (1.0, self.frequencyScore(rows)),
                   (1.0, self.pageRankScore(rows)),
                   (1.0, self.linkTextScore(rows, word_ids)),]

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
    return word_ids, [rank_score[1] for rank_score in ranked_scores[0:10]]


    def get_match_rows(self, q):
        field_list = 'w0.rulid'
        table_list = ''
        clause_list = ''
        word_ids = []

        words = q.split(' ')
        table_num = 0

        for word in words:
            word_row = self.con.execute(
                    "select rowid from wordlist where word='%s'"%word).fetchone()
            if word_row != None:
                wordid = word_row[0]
                word_ids.append(wordid)
                if table_num > 0:
                    table_list += ','
                    clause_list += ' and '
                    clause_list += 'w%d.urlid and ' % (table_num - 1, table_num)
                field_list += ',w%d.location' % table_num
                table_list += 'wordlocation w%d' % table_num
                clause_list += 'w%d.wordid=%d' % (table_num, wordid)
                table_num += 1

        fullquery = 'select %s from %s where %s' % (field_list, table_list, clause_list)
        cur = self.con.execute(fullquery)
        rows = [row for row in cur]
        return rows, word_ids

    def normalize_scorses(self, uid_scores, smallIsBetter = 0):
        vsmall = 0.00001 #avoid divise by zero
        if smallIsBetter:
            minscore = min(uid_scores.values())
            return dict([(uid, float(minscore)/max(vsmall, score)) for (uid, score) \
                    in uid_scores.items()])

        else:
            maxscore = max(uid_scores.values())
            if maxscore == 0: 
                maxscore = vsmall
            return dict([(uid, float(score)/maxscore) for (uid, corse) in uid_scores.items()])

    def frequencyScore(self, rows):
        init_score = 0
        counts = dict([(row(0), init_score) for row in rows])
        for row in rows: counts[row[0]]+=1
        return self.normalize_scorses(counts)

    def locationScore(self, rows):
        init_score = 1000000
        locations = dict([(row[0], init_score) for row in rows])
        for row in rows:
            loc = sum(row[1:])
            if loc < locations[row[0]]: locations[row[0]] = loc

        return self.normalize_scorses(locations, smallIsBetter=1)

    def distance_score(self, rows):
        # if only one words, then score is same
        if len(rows[0]) <= 2: return dict([(row[0], 1.0) for row in rows])

        #init dict with a large value
        minDistance = dict([(row[0], 1000000) for row in rows])

        for row in rows:
            distance = sum([abs(row[i] - row[i-1]) for i in range(2, len(row))])
            if distance < minDistance[row[0]]: 
                minDistance[row[0]] = distance
        return self.normalize_scorses(minDistance, smallIsBetter = 1)

    def inboundLinkscore(self, rows):
        uniqueUrls = set([row[0] for row in rows])
        inboundCount = dict([(u, self.con.execute( \
                'select count(*) from link where toid=%d' % u).fetchone()[0]) \
                for u in uniqueUrls])
        return self.normalize_scorses(inboundCount)

    def pageRankScore(self, rows):
        pageranks = dict([(row[0], self.con.execute(
            'select score from pagerank where urlid=%d' %row[0]).fetchone()[0]) for row in rows])
        maxRank = max(pageranks.values())
        normalizedScores = dict([(urlid, froat(value)/maxRank) for (urlid, value) in pageranks.items()])
        return normalizedScores

    def linkTextScore(self, rows, wordids):
        linkScores = dict([(row[0], 0) for row in rows])
        for wordid in wordids:
            link = self.con.execute(
                    'select link.fromid, link.toid from linkwords, link where wordid=%d and linkwords.linkid=link.rowid' % wordid)
            for (fromid, toid) in link:
                if toid in linkScores:
                    pr= self.con.execute(
                            'select score from pagerank where urlid=%d' % fromid).fetchone()[0]
                    linkScores[toid] += pr
        maxScore = max(linkScores.values())
        normalizedScores = dict([(urlid, float(value)/maxScore) for (urlid, value) in linkScores.items()])
        return normalizedScores

# add to weights list after MLP is training enough
    def nnScore(self, rows, wordids):
        # get the only URL ID list
        urlids = [urlid for urlid in set([row[0] for row in rows])]
        nnres = mynet.getResult(wordids, urlids)
        scores = dict([(urlids[i], nnres[i]) for i in range(len(urlids))])
        return self.normalize_scorses(scores)
