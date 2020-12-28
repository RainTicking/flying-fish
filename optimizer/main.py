#!/usr/bin/python
# -*- coding: UTF-8 -*- 
import json
import optimizer
#import sys
#sys.path.append("..")
#from app import conn



# 打开文件
sqlFo = open("json","r")
# 读取文件
sqlStr = sqlFo.read()
# 关闭打开的文件
sqlFo.close() 
# 生成Json
sqlJson = json.loads(sqlStr)


if __name__ == '__main__':
    tree = BinTree()
    for i in range(1,11):
        tree.add(i)
    tree.preOrderTraversal(tree.root)




