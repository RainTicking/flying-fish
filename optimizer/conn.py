# coding:utf-8

import pymysql
import csv
import datetime

def connect():
    """
    连接mysql数据库
    :return:
    """
    conn = pymysql.connect(host="127.0.0.1", port=3306,
                           user="hadoop", password="hadoop",
                           database="flying_fish", charset="utf8")
    return conn
 
 
def insert_mysql(read_path, table_name, fields):
    """
    本地数据插入mysql
    :param read_path:  文件路径
    :return:
    """
    csv_file = open(read_path, "r", encoding="UTF-8")
    reader_csv = csv.reader(csv_file)
    conn = connect()
    cursor = conn.cursor()
    sql = "INSERT INTO `{table}` ({field}) VALUES ({val});".format(
        table=table_name,
        field='`' + '`,`'.join(fields) + '`',
        val=','.join(['%s'] * len(fields))
    )
    value_list = []
    try:
        for line in reader_csv:
            temp_list = []
            for i in range(len(fields)-1):
                print(line[i])
                temp_list.append(line[i])
            temp_list.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            value_list.append(temp_list)
            if len(value_list) == 1024:
                cursor.executemany(sql, value_list)
                conn.commit()
                value_list = []
        if value_list:
            cursor.executemany(sql, value_list)
            conn.commit()
    except Exception as e:
        print("执行MySQL: %s 时出错：%s" % (sql, e))
    finally:
        cursor.close()
        conn.close()
        csv_file.close()
 
 
if __name__ == '__main__':
    read_path = "../data/user.csv"
    table_name = "user"
    fields = ["code", "name", "email", "password", "is_valid","create_time"]
    insert_mysql(read_path, table_name, fields)




