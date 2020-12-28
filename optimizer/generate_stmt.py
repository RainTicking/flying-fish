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

class GenerateStmt(object):
    '生成新SQL语句'
    def __init__(self,tree=None, comment=None):
        self.root = copy.deepcopy(tree.root)
        self.commentTree = copy.deepcopy(comment.root)
        self.stmt = ''
        self.pre_node = None
    # 基于树生成语句
    def generate(self, root):
        if root is None:
            return
        if root.data['type'] != 'NONTERMINAL':
            self.stmt = self.stmt + self.str_concat(self.pre_node, root)
            self.pre_node = root
        self.generate(root.left)
        self.generate(root.right)
    # 节点字符串拼接
    def str_concat(self, pre_node, root):
        if pre_node is None:
            pre_line = 1       #上一节点所在行    
            pre_column = 0     #上一节点所在行尾  
        else:
            pre_line = int(pre_node.data['last_line'])       #上一节点所在行    
            pre_column = int(pre_node.data['last_column'])   #上一节点所在行尾  
        curr_line = int(root.data['first_line'])         #当前节点所在行 
        curr_column = int(root.data['first_column'])     #当前节点所在行首
        # 是否换行
        if pre_line == curr_line:
            blank_cnt = curr_column - pre_column - 1
            curr_str = ' ' * blank_cnt + root.data['value']
            return curr_str
        else:
            line_cnt = curr_line - pre_line
            curr_str = ''
            while line_cnt > 0:
                curr_str = curr_str + self.get_comment(self.commentTree ,curr_line - line_cnt) + '\n'
                line_cnt = line_cnt - 1
            curr_str = curr_str + ' ' * curr_column + root.data['value']
            return curr_str
    # 检测上一行
    def get_comment(self, root, pre_line):
        queue = [root]
        while queue:
            node = queue.pop(0)
            if ( node.data['name'] == 'COMMENT'
                and int(node.data['first_line']) == pre_line
            ):
                return node.data['value']
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        return ''

if __name__ == '__main__':
    arg1 = sys.argv[1]
    # 打开文件
    sqlFo = open(arg1+".json","r")
    commentFo = open(arg1+".cmt","r")
    # 读取文件
    sqlStr = sqlFo.read()
    commentStr = commentFo.read()
    # 关闭打开的文件
    sqlFo.close() 
    commentFo.close() 
    # 生成Json
    sqlJson = json.loads(sqlStr)
    commentJson = json.loads(commentStr)
    # 生成二叉树
    sql_tree = BinTree(sqlJson)
    comment_tree = BinTree(commentJson)
    # 关联字段
    generatestmt = GenerateStmt(sql_tree,comment_tree)
    generatestmt.generate(generatestmt.root)
    print(generatestmt.stmt)

