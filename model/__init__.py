import pymysql
from flask_sqlalchemy import SQLAlchemy

# 数据库初始化
db = SQLAlchemy()
pymysql.install_as_MySQLdb()

