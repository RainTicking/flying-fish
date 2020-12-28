from flask import Flask, render_template, session, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import pymysql
from conn import *

app = Flask(__name__)

#flask的session需要用到秘钥字符串
app.config["SECRET_KEY"] = "a#NT(s)e!@#$%^&*(f6$w*a"

class Config(object):
    """配置参数"""
    # sqlalchemy配置参数
    SQLALCHEMY_DATABASE_URI = "mysql://hadoop:hadoop@127.0.0.1:3307/flying_fish?charset=utf8mb4"
    # 设置sqlalchemy自动跟踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True

app.config.from_object(Config)

# 创建数据库sqlalchemy工具对象
pymysql.install_as_MySQLdb() 
db = SQLAlchemy(app)


# 定义表单的模型类
class LoginForm(FlaskForm):
    """自定义的登录表单模型类"""
    #                       名字           验证器
    # DataRequired 保证数据必须填写，并且不能为空
    user_code = StringField(label=u"系统号",description="请输入系统号",validators=[DataRequired(u"请输入系统号")],render_kw={"placeholder": "系统号"})
    password = PasswordField(label=u"密码",description="请输入系统号",validators=[DataRequired(u"请输入密码")],render_kw={"placeholder": "密码"})
    submit = SubmitField(label=u"登录")


@app.before_request
def is_login(*args,**kwargs):
    '''
    如果允许通过访问，可以return None
    该装饰器装饰的函数如果有return其他内容则直接结束访问，
    效果有点类似django的process_reqeust中间件方法。
    比如通过这个装饰器写登陆验证，判断其是否有session，没有则不允许访问，有则继续访问
    然后通过request.path判断访问的函数，如果是登陆(白名单)则通过。
    request.url 是完整的url
    request.path是域名后面的url正则
    '''
    if request.path == '/login':
        return None
    user = session.get('user_code')
    if user:
        return None
    return redirect(url_for("login"))


# 登录页
@app.route("/login", methods=["GET", "POST"])
def login():
    ucode = session.get("user_code","请登录")
    # 创建表单对象,如果是post请求，前端发送了数据，flask会把数据在构造form对象的时候，存放到对象中
    form = LoginForm() 
    # 判断form中的数据是否合理    
    # 如果form中的数据完全满足所有的验证器，则返回真，否则返回假
    if form.validate_on_submit():
        # 表示验证合格
        # 提取数据
        code = form.user_code.data 
        pwd = form.password.data 
        user = User.query.filter_by(code=code).first()
        if pwd == user.password:
            session["user_code"]= code 
            return redirect(url_for("index"))
        else:
            return render_template("login.html", form=form, ucode=ucode)
    return render_template("login.html", form=form, ucode=ucode)

# 退出页
@app.route("/login_out")
def login_out():
    session.pop("user_code")
    return redirect(url_for("login"))


# 主页
@app.route("/")
def index():
    ucode = session.get("user_code","请登录")
    task_list = Task.query.order_by(Task.total_optimizers.desc()).limit(20)
    #for task in task_list:
    #    task.sql_ast_json=url_for('task_detail', id=task.task_id)
    data = {
        "ucode" : ucode,
        "task_list": task_list
    }
    return render_template("index.html", **data)


# 任务优化详情页
@app.route("/task_detail/<id>")
def task_detail(id):
    ucode = session.get("user_code","请登录")
    task = Task.query.filter_by(task_id=id).first()
    if task:
        data = {
            "ucode" : ucode,
            "original_sql" : task.sql_stmt,
            "optimized_sql" : task.optimized_sql
        }
        return render_template("task_detail.html", **data)
    else:
        return redirect(url_for("index"))



if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8000)
