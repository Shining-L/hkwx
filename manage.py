from config import config_dict
from flask_migrate import Migrate
from model import db
from applet_app import create_applet_app

"""
在manage.py文件中，实现项目的基本配置，
数据库、
迁移、
蓝图、
配置文件、
路由 
等

"""

# 配置数据链接信息

app = create_applet_app(config_dict['base'])
# 数据迁移脚本
migrate = Migrate(app, db)

@app.route('/')
def hello_world():  # put application's code here
    print(app.config['SECRET_KEY'])

    return 'Hello World!'


print(app.url_map)
