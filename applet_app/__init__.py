from flask import Flask
from models import db


def create_applet_app(config_name=None):
    app = Flask(__name__)
    # 项目配置文件
    app.config.from_object(config_name)

    # 初始化模型对象
    db.init_app(app)

    # 注册蓝图对象
    from .user import user_bp
    from .mybooks import my_books_bp
    from .category import category_bp
    from .search import search_bp
    from .book import book_bp
    from .recommend import re_bp
    from .my import my_bp
    from .reader_config import config_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(my_books_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(re_bp)
    app.register_blueprint(my_bp)
    app.register_blueprint(config_bp)

    # 导入请求钩子，用户的权限校验
    from utils.middlewares import before_request
    app.before_request(before_request)
    return app
