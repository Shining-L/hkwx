from flask import Blueprint, request, jsonify
from models import User

user_bp = Blueprint('users', __name__, url_prefix="/user")


@user_bp.route('/login', methods=['POST'])
def index():
    # 获取登陆凭证
    code = request.json.get('code', "")
    # 获取加密数据
    encrypt = request.json.get('encryptedData', "")
    # 获取加密初始化向量
    iv = request.json.get('iv', "")
    if not code or not encrypt or not iv:
        return jsonify(msg='参数有误'), 403


    return "你好,用户模块"
