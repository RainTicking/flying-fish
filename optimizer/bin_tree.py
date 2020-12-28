#!/usr/bin/python
# -*- coding: UTF-8 -*- 
import json
import copy

class TreeNode(object):
    '二叉树节点类'
    def __init__(self, data=None):
        self.data = data
        self.left = None
        self.right = None


class BinTree(object):
    '二叉树类'
    # 二叉树初始化
    def __init__(self, data = None):
        self.queue = []
        if data is None:
            self.root = None
        else:
            node = TreeNode(copy.deepcopy(data))
            self.root = node
            self.queue.append(node)
            while self.queue:
                tmpNode = self.queue[0]
                if tmpNode.data['left'] != '':
                    node = TreeNode(tmpNode.data['left'])
                    tmpNode.left = node
                    self.queue.append(node)
                    tmpNode.data['left'] = ''
                elif tmpNode.data['right'] != '':
                    node = TreeNode(tmpNode.data['right'])
                    tmpNode.right = node
                    self.queue.append(node)
                    tmpNode.data['right'] = ''
                else:
                    self.queue.pop(0)
    # 前序遍历
    def preOrderTraversal(self, root):
        # 遍历终止条件
        if root is None:
            return
        if root.data['name'] == 'join_table':
            print(root.data['name'])
        self.preOrderTraversal(root.left)
        self.preOrderTraversal(root.right)


if __name__ == '__main__':
    # 打开文件
    sqlFo = open("json","r")
    # 读取文件
    sqlStr = sqlFo.read()
    # 关闭打开的文件
    sqlFo.close() 
    # 生成Json
    sqlJson = json.loads(sqlStr)
    # 生成二叉树
    tree = BinTree(sqlJson)
    # 前序遍历
    tree.preOrderTraversal(tree.root)

