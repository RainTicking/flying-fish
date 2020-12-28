
drop database flying_fish;
create database flying_fish DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

安装虚拟环境：
python3 -m venv venv
source venv/bin/activate

安装python包：

pip install flask
pip install gunicorn
pip install flask_sqlalchemy
pip install flask_wtf
pip install pymysql


