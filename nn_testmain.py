#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# File Name: nn_testmain.py
# Author: lpqiu
# mail: qlp_1018@126.com
# Created Time: 2014年08月14日 星期四 21时42分18秒
#########################################################################
import nn

if __name__ == "__main__":
    print("go!!!")
    mynet = nn.SearchNet('nn.db')
    mynet.createTables()
    wWorld, wRiver, wBank = 101, 102, 103
    uWorldBank, uRiver, uEarth = 201, 202, 203
    mynet.generateHiddenNode([wWorld, wBank], [uWorldBank, uRiver, uEarth])
    for c in mynet.con.execute('select * from wordhidden'): print(c)
    for c in mynet.con.execute('select * from hiddenurl'): print(c)
    
