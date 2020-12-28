# coding:utf-8

# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# import pymysql
import datetime
from main import db 

# 设置连接数据库的URL
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://hadoop:hadoop@127.0.0.1:3306/test'

# 设置每次请求结束后会自动提交数据库中的改动
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# 跟踪数据库中的变动
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 查询时会显示原始SQL语句
# app.config['SQLALCHEMY_ECHO'] = True

# 创建数据库sqlalchemy工具对象
# pymysql.install_as_MySQLdb() 
# db = SQLAlchemy()


# 创建数据库模型类
class User(db.Model):
    """用户表"""
    __tablename__ = "user" # 指明数据库的表名，用户表
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # 整形的主键，会默认设置为自增主键
    code = db.Column(db.Integer, index=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(128))
    password = db.Column(db.String(128))
    is_valid = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
   # role_id = db.Column(db.Integer, db.ForeignKey("column_distribution.id"))

class Table(db.Model):
    """元数据表"""
    __tablename__ = "table"  #元数据表

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    db_name = db.Column(db.String(32), index=True)
    tbl_name = db.Column(db.String(32), index=True)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

class TablePartition(db.Model):
    """表分区"""
    __tablename__ = "table_partition"  #表分区

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    db_name = db.Column(db.String(32), index=True)
    tbl_name = db.Column(db.String(32), index=True)
    partition_name = db.Column(db.String(32), index=True)
    numFiles = db.Column(db.Integer)
    numRows = db.Column(db.Integer)
    rawDataSize = db.Column(db.Integer)
    totalSize = db.Column(db.Integer)
    transient_lastDdlTime = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)


class ColDistr(db.Model):
    """字段数据分布表"""
    __tablename__ = "column_distribution"  #字段分布

    id = db.Column(db.Integer, primary_key=True)
    db_name = db.Column(db.String(32), index=True)
    tbl_name = db.Column(db.String(32), index=True)
    col_name = db.Column(db.String(32), index=True)
    data_type = db.Column(db.String(32), index=True)
    skew_key = db.Column(db.String(32))
    skew_key_rows = db.Column(db.Integer)
    min_val =  db.Column(db.String(32))
    max_val =  db.Column(db.String(32))

class Task(db.Model):
    """任务表"""
    __tablename__ = "task"  #任务表

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, index=True)
    task_name_en = db.Column(db.String(64), index=True)
    task_name_cn = db.Column(db.String(64), index=True)
    task_description = db.Column(db.Text)
    task_type = db.Column(db.String(32))
    owner_code = db.Column(db.Integer, index=True)
    owner_name = db.Column(db.String(32))
    run_duration = db.Column(db.String(32))
    total_optimizers =  db.Column(db.Integer)
    sql_stmt = db.Column(db.Text)
    sql_ast_json = db.Column(db.Text)
    optimized_sql = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now ,onupdate=datetime.datetime.now)



if __name__ == '__main__':

    # app = Flask(__name__)
    # app.config.from_object(Config)

    # 创建数据库sqlalchemy工具对象
    # pymysql.install_as_MySQLdb() 
    # db = SQLAlchemy(app)

    # 清除数据库里的所有数据
    db.drop_all()

    # 创建所有的表
    db.create_all()

    # 创建对象
    # role1 = Role(name="admin")
    # session记录对象任务
    # db.session.add(role1)
    # 提交任务到数据库中
    # db.session.commit()

    # role2 = Role(name="stuff")
    # db.session.add(role2)
    # db.session.commit()

    us1 = User(code = 20241606, name='a',  email='yu@abc.com',      password='123456', is_valid = 1)
    us2 = User(code = 26566395, name='b',  email='chen@abc.com',    password='123456', is_valid = 1)
    us3 = User(code = 26606569, name='c',  email='ji@abc.com',      password='123456', is_valid = 1)
    us4 = User(code = 20238746, name='d',  email='li@abc.com',      password='123456', is_valid = 1)
    us5 = User(code = 26013356, name='e',  email='liu@abc.com',     password='123456', is_valid = 1)
    us6 = User(code = 23005185, name='f',  email='sun001@abc.com',  password='123456', is_valid = 1)
    us7 = User(code = 23113703, name='g',  email='zhu@abc.com',     password='123456', is_valid = 1)

    # 一次保存多条数据
    db.session.add_all([us1,us2,us3,us4,us5,us6,us7])
    db.session.commit()




