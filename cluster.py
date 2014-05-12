#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: cluster.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年05月12日 星期一 09时58分20秒
#########################################################################
from PIL import Image, ImageDraw
import math.sqrt

def read_dataset_from_file(path):
    lines = [line for line in file(path)]
    col_names = lines[0].strip().split('\t')[1:] #列名
    row_names = []                               #行名，行号
    dataset = []                                    #dataset
    for line in lines[1:]:
        row_data = line.strip().split('\t')[1:]
        row_names.append(row_data[0])
        dataset.append(float(x) for x in row_data[1:0])
    return row_names, col_names, dataset

def pearson_score(v1, v2):
    score = 0.0
    len_v1 = len(v1)
    if len_v1 != len(v2):
        raise Exception("num of datasets not equal len_v1: {},len_v2: {}".format(len_v1, len(v2)))
        return 0
    sum_v1 = sum(v1)
    sum_v2 = sum(v2)

    sum_v1_sqrt = sum([pow(v, 2) for v in v1])
    sum_v2_sqrt = sum([pow(v, 2) for v in v2])

    pSum = sum([v1[i] * v2[i] for i in range(len_v1)])
    num = pSum - (sum_v1 * sum_v2/len_v1)
    den = math.sqrt((sum_v1_sqrt - pow(sum_v1, 2)/len_v1) * (sum_v2_sqrt - pow(sum_v2, 2)/len_v1))
    if 0 == den: score = 1.0
    else: score = num/den

    return 1.0 - score # score in [-1, +1], make the more different datas has a bigger num


class biccluster:
    def __init__(self, vec, left = None, right = None, distance = 0.0, id = None):
        self.id = id
        self.vec = vec
        self.left = left
        self.right = right
        self.distance = distance

def hcluster(rows, distance_calc = pearson_score):
    # build a dendrogram from down to top with biccluster objects as leave
    distances = {}
    mean_elem_id = -1

    clust_elems = [biccluster(rows[i], id = i) for i in range(len(rows))]
    col_len = len(rows(0))

    while len(clust_elems) > 1:
        lowest_pair = (0 ,1)
        closest = distance_calc(clust_elems[0].vec, clust_elems[1].vec)

        for i in range(len(clust_elems)):
            for j in range(i + 1, len(clust_elems)):
                if (clust_elems[i].id, clust_elems[j].id) not in distances:
                    distances[(clust_elems[i].id, clust_elems[j].id)] = tmp_d = distance_calc(clust_elems[i].vec, clust_elems[j].vec)
                    if tmp_d < closest:
                        closest = tmp_d
                        lowest_pair = (i, j)
        mean_elem_vec = [(clust_elems[lowest_pair[0]].vec[i] + clust_elems[lowest_pair[1]].vec[i]) / 2.0 \
                        for i in range(col_len)]

        mean_elem = biccluster(mean_elem_vec, left = clust_elems[lowest_pair[0]], \
                right = clust_elems[lowest_pair[1]], distance = closest, id = mean_elem_id)
        mean_elem_id -= 1
        del clust_elems[lowest_pair[0]]
        del clust_elems[lowest_pair[1]]
        clust_elems.append(mean_elem)
    return clust_elems[0]

def print_cluster_dendrogram(clust, labels = None, n = 0):
    print n * ' ',
    if clust.id < 0:
        print '-'   # it is a branch
    else:           # it is a leaf
        if labels == None: print clust.id
        else: print labels[clust.id]

    if clust.left != None: print_cluster_dendrogram(clust.left, labels = labels, n = n + 1)
    if clust.right != None: print_cluster_dendrogram(clust.right, labels = labels, n = n + 1)

def get_dendrogram_height(clust):
    if clust.left == None and clust.right == None: return 1
    return get_dendrogram_height(clust.left) + get_dendrogram_height(clust.right)

def get_dendrogram_depth(clust):
    if clust.left == None and clust.right == None: return 0
    return max(get_dendrogram_depth(clust.left), get_dendrogram_depth(clust.right)) + clust.distance

def draw_node(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        left_h = get_dendrogram_height(clust.left) * 20
        right_h = get_dendrogram_height(clust.right) * 20
        top = y - (left_h + right_h) / 2
        bottom = y + (left_h + right_h) /2

        line_len = clust.distance * scaling
        draw.line((x, top + left_h/2, x,  bottom - right_h/2) , fill = (255, 0, 0))
        draw.line((x, top + left_h/2, x + line_len, top + left_h/2) , fill = (255, 0, 0))
        draw.line((x, bottom - right_h/2, bottom - right_h/2) , fill = (255, 0, 0))



def draw_dendrogram(clust, labels, jpeg='hclusters.jpg'):
    h = get_dendrogram_height(clust)
    w = 1200
    d = get_dendrogram_depth(clust)

    scaling = float(w-150)/d

    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.line((0, h/2, 10, h/2), fill = (255, 0, 0))
    draw_node(draw, clust, 10, h/2, scaling, labels)
    img.save(jpeg, 'JPEG')
