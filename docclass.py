#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: docclass.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年08月23日 星期六 03时24分16秒
#########################################################################
import math
import re

def getWords(doc):
    splitter = re.compile('\\W*')
    # split if it is not word
    words = [s.slower() for s in splitter.split(doc)
            if len(s) > 2 and len(s) < 20]

    return dict([(w, 1) for w in words])

class Classifier:
    def __init__(self, get_features_fun, filename = None):
        # {'feature1':{'class1': class1_docs_nums_with_this_feature, 'class2': class2_docs_nums_with_this_feature}, ...}
        self.fc = {}
        # class : doc
        self.cc = {}
        self.get_features = get_features_fun
        self.thresholds = {}

    def getThresholds(self, cat):
        if cat not in self.thresholds:
            return 1.0
        else:
            return self.thresholds[cat]

    def setThreshold(self, cat,t):
        self.thresholds[cat] = t

    def incFc(self, f, cat):
        self.fc.setdefault(f, {})
        self.fc[f].setdefault(cat, 0)
        self.fc[f][cat] += 1

    def incCc(self, cat):
        self.cc.setdefault(cat, 0)
        self.cc[cat] += 1

    def getFcCount(self, f, cat):
        if f in self.fc and cat in self.fc[f]:
            return float(self.fc[f][cat])
        return 0.0

    def getCatCount(self, cat):
        if cat in self.cc:
            return float(self.cc[cat])
        return 0

    def totalCount(self):
        return sum(self.cc.values())

    def categories(self):
        return self.cc.keys()

    def train(self, item, cat):
        features = self.get_features(item)
        for f in features:
            self.incf(f, cat)

        self.incc(cat)

    def fprob(self, f, cat):
        if self.getCatCount(cat) == 0: 
            return 0
        else:
            return self.getFcCount(f, cat)/self.getCatCount(cat)

    def weightedProb(self, f, cat, prf, weight = 1.0, ap = 0.5):
        # calc current frequence
        basic_prob = prf(f, cat)

        # static apperance times of the feature in all docs
        totals = sum([self.getFcCount(f, c) for c in self.categories()])
        bp  = ((weight * ap) + (totals * basic_prob))/(weight + totals)
        return bp

    def classify(self, item, default = None):
        probs ={}

        # find the max frequence class
        max = 0.0
        for cat in self.categories():
            probs[cat] = self.fprob(item, cat)
            if probs[cat] > max:
                max = probs[cat]
                best = cat

        # make sure beyond the threshold * times
        for cat in probs:
            if cat == best:
                continue
            if probs[cat] * self.getThresholds(best):
                return default

        return best

class NaiveBayes(Classifier):
    def docProb(self, item, cat):
        features = self.get_features(item)

        p = 1
        for f in features:
            p *= self.weightedProb(f, cat, self.fprob)
        return p

    def prob(self, item, cat):
        catProb = self.getCatCount(cat)/self.totalCount()
        docProb = self.docProb(item, cat)
        return docProb * catProb

class FisherClassifier(Classifier):
    def __init__(self, get_features_fun):
        Classifier.__init__(self, get_features_fun)
        self.mininums = {}

    def setMininum(self, cat, min):
        self.mininums[cat] = min

    def getMininum(self, cat):
        if cat not in self.mininums:
            return 0
        else:
            return self.mininums[cat]

    def cprob(self, f, cat):
        clf = self.fprob(f, cat)
        if clf == 0:
            return 0

        freq_sum = sum([self.fprob(f, c) for c in self.categories()])
        p = clf/freq_sum

        return p

    def invchi2(self, chi, df):
        m = chi / 2.0
        sum = term = math.exp(-m)
        for i in range(1, df/2):
            term *= m / i
            sum += term
        return min(sum, 1.0)


    def fisherProb(self, item, cat):
        # multiplate prob
        p = 1
        features = self.get_features(item)
        for f in features:
            p *= self.weightedProb(f, cat, self.cprob)

        fscore = -2 * math.log(p)

        return self.invchi2(fscore, len(features) * 2)

    def classify(self, item, default = None):
        best = default
        max = 0.0
        for c in self.categories():
            p = self.fisherProb(item, c)
            if p > self.getMininum(c) and p > max:
                best = c
                max = p
        return best

def sampleTrain(classifier):
    classifier.train('Nobody owns the water.', 'good')
    classifier.train('the quick rabbit jumps fences', 'good')
    classifier.train('buy pharmaceuticals now', 'bad')
    classifier.train('make quick money in the online casino', 'bad')
    classifier.train('the quick brown fox jumps', 'good')


if __name__ == "__main__":
    spamer = Classifier(getWords)
    spamer.train('the quick brown fox jumps over the lazy dog', 'good')
    spamer.train('make quick money in the online casino', 'bad')
    spamer.fcount('quick', 'good')
    spamer.fcount('quick', 'bad')
