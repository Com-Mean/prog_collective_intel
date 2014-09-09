#!/usr/bin/env python

# -*- coding: utf-8 -*-
#########################################################################
# File Name: trees.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年08月28日 星期四 17时10分22秒
#########################################################################
from math import log
import operator

def createDataSet():
    dataSet = [[1, 1, 'yes'],
               [1, 1, 'yes'],
               [1, 0, 'no' ],
               [0, 1, 'no' ],
               [0, 1, 'no' ],]

    labels = ['no surfacing', 'flippers']

    return dataSet, labels

#节点划分前的熵
def calcShannonEnt(dataSet):
    numEntries = len(dataSet)
    labelCounts = {}

    for feaVec in dataSet:
        currentLabel = feaVec[-1]
        if currentLabel not in labelCounts.keys():
            labelCounts[currentLabel] = 0
        labelCounts[currentLabel] += 1

    shannonEnt = 0.0
    for key in labelCounts.keys():
        prob = float(labelCounts[key])/numEntries
        shannonEnt -= prob * log(prob, 2)

    return shannonEnt

def splitDataSet(dataSet, axis, value):
    retDataSet = []
    for feaVec in dataSet:
        if feaVec[axis] == value:
            reducedFeaVec = feaVec[:axis]
            reducedFeaVec.extend(feaVec[axis+1:])
            retDataSet.append(reducedFeaVec)
    return retDataSet

def chooseBestFeatureToSplit(dataSet):
    numFeatures = len(dataSet[0]) - 1
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0; bestFeature = -1
    for i in range(numFeatures):
        featList = [example[i] for example in dataSet]
        uniqueVals = set(featList)
        newEntropy = 0.0
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet)/ float(len(dataSet))
            newEntropy += prob * calcShannonEnt(subDataSet)#划分后的熵
        #calc信息增益,既然划分前的熵一样，应该可以节约这一步，找到最小的划分后的熵即为最佳的划分点
        infoGain = baseEntropy - newEntropy 
        if infoGain > bestInfoGain:
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature

def majorityCnt(classList):
    classCount = {}
    for vote in classList:
        if vote not in classCount.keys(): classCount[vote] = 0
        classCount[vote] += 1

    sortedClassCount = sorted(classCount.iteritems(), \
            key = operator.itemgetter(1), reverse = True)
    return sortedClassCount[0][0]

def createTree(dataSet, labels):
    classList = [example[-1] for example in dataSet]

    if classList.count(classList[0]) == len(classList):
        return classList[0]

    if len(dataSet[0]) == 1:
        return majorityCnt(classList)

    bestFeat = chooseBestFeatureToSplit(dataSet)
    bestFeatLabel = labels[bestFeat]
    myTree = {bestFeatLabel:{}}
    del(labels[bestFeat])
    featValues = [example[bestFeat] for example in dataSet]
    uniqueVals = set(featValues)

    for value in uniqueVals:
        subLabels = labels[:]
        myTree[bestFeatLabel][value] = createTree(splitDataSet\
                (dataSet, bestFeat, value), subLabels)

    return myTree

def classify(inputTree, featLabels, testVec):
    firstStr = inputTree.keys()[0]
    secondDict = inputTree[firstStr]
    featIndex = featLabels.index(firstStr)
    for key in secondDict.keys():
        if testVec[featIndex] == key:
            if type(secondDict[key]).__name__ == 'dict':
                classLabel = classify(secondDict[key], featLabels, testVec)
            else: classLabel = secondDict[key]
    return classLabel

def storeTree(inputTree, filename):
    import pickle
    fw = open(filename, 'w')
    pickle.dump(inputTree, fw)
    fw.close()

def grabTree(filename):
    import pickle
    fr = open(filename)
    return pickle.load(fr)

if __name__ == '__main__':
    myDat, labels = createDataSet()
    shannonEnt = calcShannonEnt(myDat)
    print('myDat:%s\nlabels:%s\nshannonEnt:%f' % \
            (myDat, labels, shannonEnt))
    myTree = createTree(myDat, labels)
    print('myTree:', myTree)