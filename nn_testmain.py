#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: nn_testmain.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年08月14日 星期四 21时42分18秒
#########################################################################
import os
import nn

if __name__ == "__main__":
    print("go!!!")
    os.unlink('nn.db')
    mynet = nn.SearchNet('nn.db')
    mynet.createTables()
    wWorld, wRiver, wBank = 101, 102, 103
    uWorldBank, uRiver, uEarth = 201, 202, 203
    allInput = list((wWorld, wRiver, wBank))
    allUrls = list((uWorldBank, uRiver, uEarth))
    mynet.generateHiddenNode([wWorld, wBank], allUrls)
    for c in mynet.con.execute('select * from wordhidden'): print(c)
    for c in mynet.con.execute('select * from hiddenurl'): print(c)
    mynet.trainQuery([wWorld, wBank], allUrls, uWorldBank)
    print(mynet.getResult([wWorld, wBank], allUrls))

    for i in range(30):
        mynet.trainQuery([wWorld, wBank], allUrls, uWorldBank)
        mynet.trainQuery([wRiver, wBank], allUrls, uRiver)
        mynet.trainQuery([wWorld], allUrls, uEarth)

    print(mynet.getResult([wWorld, wBank], allUrls))
    print(mynet.getResult([wRiver, wBank], allUrls))
    print(mynet.getResult([wBank], allUrls))
