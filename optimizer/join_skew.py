#!/usr/bin/python
# -*- coding: UTF-8 -*- 
import json
import copy
import sys 
import generate_stmt
import pymysql
import datetime

sys.setrecursionlimit(3000)  # 将Python递归深度修改为3000,默认为1000

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


class JoinSkew(object):
    'Join倾斜类'
    def __init__(self,tree=None):
        self.root = copy.deepcopy(tree.root)
        self.joinKeyList = []     # 关联字段
        self.total_optimizers = 0
    # 前序遍历获取单条SELECT语句
    def preOrderTraversal(self, root):
        # 遍历终止条件
        if root is None:
            return
        if root.data['name'] == 'single_select_stmt':
            self.join(root)
        self.preOrderTraversal(root.left)
        self.preOrderTraversal(root.right)
    # Join关联处理
    def join(self, root):
        joinQueue = self.getJoinNode(root)  #join_table节点列表
        joinConditionQueue = []  #join_condition节点列表
        tableFactorQueue = []  #table_factor节点列表
        # 生成join_condition节点列表
        for i, val in enumerate(joinQueue):
            if val.left.right.right.right.data['name'] == 'join_condition':
                joinConditionQueue.append(val.left.right.right.right)
            elif val.left.right.right.right.right.data['name'] == 'join_condition':
                joinConditionQueue.append(val.left.right.right.right.right)
        # 生成table_factor节点列表
        for i, val in enumerate(joinQueue):
            if val.left.right.right.right.data['name'] == 'table_factor':
                tableFactorQueue.append(val.left.right.right.right)
            elif val.left.right.right.data['name'] == 'table_factor':
                tableFactorQueue.append(val.left.right.right)
            if val.left.left.data['name'] == 'table_factor':
                tableFactorQueue.append(val.left.left)
        # 获取关联字段信息
        while joinConditionQueue:
            joinCondition = joinConditionQueue.pop(0)
            self.getJoinColumn(joinCondition,tableFactorQueue)
    # 相同层级的join_table节点
    def getJoinNode(self, root):
        join_table = None
        joinQueue = []
        if root.left.right.right.right.data['name'] == 'table_references':
            join_table = root.left.right.right.right.left.left
        elif root.left.right.right.right.right.data['name'] == 'table_references':
            join_table = root.left.right.right.right.right.left.left
        # Join节点
        while join_table.data['name'] == 'join_table':
            joinQueue.append(join_table)
            join_table = join_table.left.left
        return joinQueue
    def getJoinColumn(self,root,tableFactorQueue):
        # 左右关联条件 from() tbl_1 join () tbl_2 on tbl_1.col_1 = tbl_2.col_2
        if (root.left.right.left.right.data['name'] == 'COMPARISON'
            and root.left.right.left.left.left.left.right.data['name'] == 'DOT'
        ):
            tbl_alias = root.left.right.left.left.left.left.data['value']
            col_alias = root.left.right.left.left.left.left.right.right.data['value']
            # print("left_tbl=%s"  % tbl_alias)
            # print("left_col=%s"  % col_alias)
            joinTable = self.getJoinTable(tableFactorQueue,tbl_alias,col_alias)
            if joinTable is not None:
                joinKey = {'tbl_alias':tbl_alias,'col_alias':col_alias, 'join_node':root.left.right.left.left.left.left}
                joinKey.update(joinTable)
                self.joinKeyList.append(joinKey)
        if (root.left.right.left.right.data['name'] == 'COMPARISON' 
            and root.left.right.left.right.right.left.left.left.right.data['name'] == 'DOT'
        ):
            tbl_alias = root.left.right.left.right.right.left.left.left.data['value']
            col_alias = root.left.right.left.right.right.left.left.left.right.right.data['value']
            # print("right_tbl=%s" % tbl_alias)
            # print("right_col=%s" % col_alias)
            joinTable = self.getJoinTable(tableFactorQueue,tbl_alias,col_alias)
            if joinTable is not None:
                joinKey = {'tbl_alias':tbl_alias,'col_alias':col_alias, 'join_node':root.left.right.left.right.right.left.left.left}
                joinKey.update(joinTable)
                self.joinKeyList.append(joinKey)
    # 获取Join Table的表名及其字段名
    def getJoinTable(self,tableFactorQueue,tbl_alias,col_alias):
        myQueue = copy.deepcopy(tableFactorQueue)
        while myQueue:
            tableNode = myQueue.pop(0)
            # 获取table_factor的表及其字段
            if self.getTableColumn(tableNode,tbl_alias,col_alias) is not None:
                return self.getTableColumn(tableNode,tbl_alias,col_alias)
    # 获取table_factor里的表及其字段
    def getTableColumn(self,root,tbl_alias,col_alias):
        if (root.left.data['name'] == 'table_name'
            and root.left.right.data['name'] == 'opt_as_table'
            and root.left.left.right.data['name'] == 'DOT'
            and 
            (
                (
                    root.left.right.left.data['name'] == 'VAR'
                    and root.left.right.left.data['value'].lower() == tbl_alias.lower()
                )
                or
                (
                    root.left.right.left.right.data['name'] == 'VAR'
                    and root.left.right.left.right.data['value'].lower() == tbl_alias.lower()
                )
            )
        ):
            db_name  = root.left.left.data['value'].lower()
            tbl_name = root.left.left.right.right.data['value'].lower()
            col_name = col_alias.lower()
            return {'db_name':db_name,'tbl_name':tbl_name,'col_name':col_name}
        elif (root.left.data['name'] == 'table_subquery'
            and
            (
                (
                    root.left.right.data['name'] == 'VAR'
                    and root.left.right.data['value'].lower() == tbl_alias.lower()
                )
                or
                (
                    root.left.right.right is not None
                    and root.left.right.right.data['name'] == 'VAR'
                    and root.left.right.right.data['value'].lower() == tbl_alias.lower()
                )
            )
            and root.left.left.right.left.left.right.data['name'] == 'select_expr_list' 
            and root.left.left.right.left.left.right.right.right.data['name'] == 'table_references' 
            and root.left.left.right.left.left.right.right.right.left.left.left.data['name'] == 'table_name' 
            and root.left.left.right.left.left.right.right.right.left.left.left.left.right.data['name'] == 'DOT'
        ):
            db_name  = root.left.left.right.left.left.right.right.right.left.left.left.left.data['value'].lower()
            tbl_name = root.left.left.right.left.left.right.right.right.left.left.left.left.right.right.data['value'].lower()
            select_expr_list = root.left.left.right.left.left.right
            while select_expr_list:
                if (
                    select_expr_list.left.left.right is not None
                    and select_expr_list.left.left.right.data['name'] == 'opt_as_column'
                    and
                    (
                        select_expr_list.left.left.right.left.data['value'].lower() == col_alias.lower()
                        or 
                        (
                            select_expr_list.left.left.right.left.right is not None
                            and select_expr_list.left.left.right.left.right.data['value'].lower() == col_alias.lower()
                        )
                    )
                    and select_expr_list.left.left.left.left.data['name'] == 'column'
                ):
                    if select_expr_list.left.left.left.left.left.right is not None:
                        col_name = select_expr_list.left.left.left.left.left.right.right.data['value'].lower()
                        return {'db_name':db_name,'tbl_name':tbl_name,'col_name':col_name}
                    else:
                        col_name = select_expr_list.left.left.left.left.left.data['value'].lower()
                        return {'db_name':db_name,'tbl_name':tbl_name,'col_name':col_name}
                elif (
                    select_expr_list.left.left.right is None
                    and select_expr_list.left.left.left.left.data['name'] == 'column'
                ):
                    if (select_expr_list.left.left.left.left.left.right is not None 
                        and select_expr_list.left.left.left. left.left.right.right.data['value'].lower() == col_alias.lower()
                    ):
                        col_name = select_expr_list.left.left.left.left.left.right.right.data['value'].lower()
                        return {'db_name':db_name,'tbl_name':tbl_name,'col_name':col_name}
                    elif select_expr_list.left.left.left.left.left.data['value'].lower() == col_alias.lower():
                        col_name = select_expr_list.left.left.left.left.left.data['value'].lower()
                        return {'db_name':db_name,'tbl_name':tbl_name,'col_name':col_name}
                if select_expr_list.left.right is not None:
                    select_expr_list = select_expr_list.left.right.right
                else:
                    select_expr_list = None
    # 对SQL 进行优化
    def optimize(self, skew_key_list):
        for node in self.joinKeyList:
            for skew_key in skew_key_list:
                if node['db_name']+'.'+node['tbl_name']+'.'+node['col_name'] == skew_key[0]+'.'+skew_key[1]:
                    self.total_optimizers = self.total_optimizers + 1
                    node['join_node'].data['value'] = 'if(' + node['join_node'].data['value']
                    if skew_key[2] == '':
                        # print(node['join_node'].right.right.data['value'] + "='',concat('randstr#2@1!*4',10000*rand())," + node['tbl_alias'] + "." + node['col_alias'] +")")
                        node['join_node'].right.right.data['value'] = node['join_node'].right.right.data['value'] + "='',concat('randstr#2@1!*4',10000*rand())," + node['tbl_alias'] + "." + node['col_alias'] +")"
                    else:
                        # print(node['join_node'].right.right.data['value'] + "=" + skew_key[2] + ",cast(-10000-10000*rand() as bigint)," + node['tbl_alias'] + "." + node['col_alias'] +")")
                        node['join_node'].right.right.data['value'] = node['join_node'].right.right.data['value'] + "=" + skew_key[2] + ",cast(-10000-10000*rand() as bigint)," + node['tbl_alias'] + "." + node['col_alias'] +")"


def connect():
    """
    连接mysql数据库
    :return:
    """
    conn = pymysql.connect(host="127.0.0.1", port=3307,
                           user="hadoop", password="hadoop",
                           database="flying_fish", charset="utf8")
    return conn
 
def insert_mysql(table_name, fields, val_list):
    """
    本地数据插入mysql
    :param read_path:  文件路径
    :return:
    """
    conn = connect()
    cursor = conn.cursor()
    sql = "INSERT INTO `{table}` ({field}) VALUES ({val});".format(
        table=table_name,
        field='`' + '`,`'.join(fields) + '`',
        val=','.join(['%s'] * len(fields))
    )
    value_list = []
    try:
        temp_list = val_list
        temp_list.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        temp_list.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        value_list.append(temp_list)
        cursor.executemany(sql, value_list)
        conn.commit()
    except Exception as e:
        print("执行MySQL: %s 时出错：%s" % (sql, e))
    finally:
        cursor.close()
        conn.close()
 
 


if __name__ == '__main__':
    arg1 = sys.argv[1]
    arg_list = arg1.split('\t')
    print(arg_list)
    skew_key_list = []
    # 打开文件
    sqlO = open(arg_list[1]+".sql","r")
    sqlFo = open(arg_list[1]+".json","r")
    commentFo = open(arg_list[1]+".cmt","r")

    with open("Skewkeylist","r") as f:
        for line in f.read().splitlines():
            join_key = line.split('\t')
            skew_key_list.append(join_key)
    # 读取文件
    sql = sqlO.read()
    sqlStr = sqlFo.read()
    commentStr = commentFo.read()
    # 关闭打开的文件
    sqlFo.close() 
    commentFo.close() 
    # 生成Json
    sqlJson = json.loads(sqlStr)
    commentJson = json.loads(commentStr)
    # 生成二叉树
    tree = BinTree(sqlJson)
    comment_tree = BinTree(commentJson)
    # 关联字段
    joinskew = JoinSkew(tree)
    joinskew.preOrderTraversal(joinskew.root)
    #while joinskew.joinKeyList:
    #    print(joinskew.joinKeyList.pop(0))
    joinskew.optimize(skew_key_list)

    generatestmt = generate_stmt.GenerateStmt(joinskew,comment_tree)
    generatestmt.generate(generatestmt.root)

    table_name = "task"
    fields = ["task_id", "task_name_en", "task_name_cn", "task_description", "task_type","owner_code","owner_name","run_duration","total_optimizers","sql_stmt","sql_ast_json","optimized_sql","create_time","update_time"]
    val_list = arg_list
    val_list.append(joinskew.total_optimizers)
    val_list.append(sql)
    val_list.append("")
    val_list.append(generatestmt.stmt)
    insert_mysql(table_name, fields, val_list)

