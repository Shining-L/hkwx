from flask import Flask
from model import db


def create_applet_app(config_name=None):
    app = Flask(__name__)
    # 项目配置文件
    app.config.from_object(config_name)

    # 初始化模型对象
    db.init_app(app)

    # 注册蓝图对象
    from .user import user_bp
    app.register_blueprint(user_bp)

    return app