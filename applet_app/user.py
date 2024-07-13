from flask import Blueprint

user_bp = Blueprint('users', __name__, url_prefix="/users")

@user_bp.route('/')
def index():
    return "你好,用户模块"


