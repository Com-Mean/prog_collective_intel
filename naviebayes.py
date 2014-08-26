#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: naviebayes.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年08月26日 星期二 07时04分46秒
#########################################################################
# Using matrix will be more suitable

import math

class NaiveBayesClassifier:
    def __init__(self, attrs, attr_vrange, train_set):
        self.attrs = attrs                  #list 
        self.attr_vrange = attr_vrange
        self.category_vrange = self.attr_vrange[-1].value()
        self.train_set = train_set
        self.train_set_len = len(self.train_set)
        self.category_dataset = dict((cat, []) for cat in self.category_vrange)

    def dataCheck(self, data_set):
        for data in data_set:
            if data[-1] not in self.category_vrange:
                return False

        return True

    def getAttrvFrequency(self, dataset, attr_index, attr_value):
        attr_value_num = 0
        for data in dataset:
            if data[attr_index] == attr_value:
                attr_value_num += 1
        return attr_value_num/len(dataset)

    def getCategoryTrainset(self, train_set, category):
        category_trainset = []
        for data in train_set:
            if data[-1] == category:
                category_trainset.append(data)

        return category_trainset

    def getCategoryProb(self, category_dataset):
        prior_prob = len(category_dataset) / self.train_set_len
        posterior_prob = 1
        for attr_index in range(self.attrs):
            for attr_v in self.attr_vrange[self.attrs[attr_index]]:
                posterior_prob *= self.getAttrvFrequency(category_dataset, attr_index, attr_v)
        return prior_prob * posterior_prob

    def training(self):
        for category in self.category_vrange:
            self.category_dataset[category] += self.getCategoryTrainset(self.train_set, category)

    def classify(self, dataset_toclass):
        labeled_dataset = {}
        for data in dataset_toclass:
            max_probability = 0
            category_labeled = None
            for category in self.category_vrange:
                tmp_prob = self.getCategoryProb(self.category_dataset[category])
                if tmp_prob > max_probability:
                    max_probability = tmp_prob
                    category_labeled = category
            labeled_dataset[data] = category_labeled
        return labeled_dataset

if __name__ == "__main__":
    attrs = ['HadHouse', 'MaritalStatus', 'LoanDefault']
    attrs_vrange = {attrs[0]:['Yes','No'], attrs[1]:['Married', 'Single', 'Divorced'], attrs[2]:['Yes', 'No']}
    train_dataset = [ [attrs_vrange[attrs[0]][0], attrs_vrange[attrs[1]][1], attrs_vrange[attrs[2]][0]],
                      [attrs_vrange[attrs[0]][1], attrs_vrange[attrs[1]][0], attrs_vrange[attrs[2]][0]],
                      [attrs_vrange[attrs[0]][1], attrs_vrange[attrs[1]][1], attrs_vrange[attrs[2]][0]],
                      [attrs_vrange[attrs[0]][0], attrs_vrange[attrs[1]][0], attrs_vrange[attrs[2]][0]],
                      [attrs_vrange[attrs[0]][1], attrs_vrange[attrs[1]][2], attrs_vrange[attrs[2]][1]],]
    
    dataset_WantedLabeled = []
    loanDefaultForcast = NaiveBayesClassifier(attrs, attrs_vrange, train_dataset)
    loanDefaultForcast.training()
    loanDefaultForcast.classify(dataset_WantedLabeled)
