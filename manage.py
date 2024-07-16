from config import config_dict
from flask_migrate import Migrate
from models import db
from applet_app import create_applet_app

"""
● 在pycharm中新建hkwx_backend项目
● 在pycharm中选择创建的虚拟环境python解释器
● 创建项目启动文件manage.py，实现Flask的基本程序
● 在manage.py文件中，实现项目的基本配置，数据库、迁移等
● 配置文件、蓝图、工厂函数
● 把代码进行拆分
● 后续根据具体的功能，新创建文件或文件夹
"""

# 配置数据链接信息

app = create_applet_app(config_dict['base'])
# 数据迁移脚本
migrate = Migrate(app, db)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


print(app.url_map)
