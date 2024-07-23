from datetime import datetime, timedelta
from utils.decoraters import login_required
from flask import Blueprint, request, jsonify, current_app
from utils import jwt_utils, wxauth
from models import User, db

user_bp = Blueprint('users', __name__, url_prefix="/user")


# 封装token有效的工具 有效期24小时
def _generate_jwt_token(user_id):
    # user_id 生成token的息。
    # 生成过期时间载荷中存储的用户信息

    # 生成当前时间
    now = datetime.now()
    expiry = now + timedelta(hours=current_app.config['JWT_EXPIRE_TIME'])
    # 调用jwt工具，传入过期时间
    token = jwt_utils.generate_jwt({'user_id': user_id}, expire=expiry)
    return token


@user_bp.route('/login', methods=['POST'])
def index():
    # 获取登陆凭证
    code = request.json.get('code', "")
    # 获取加密数据
    encrypt_data = request.json.get('encryptedData', "")
    # 获取加密初始化向量
    iv = request.json.get('iv', "")
    if not code or not encrypt_data or not iv:
        return jsonify(msg='参数有误'), 403

    data = wxauth.get_wxapp_session_key(code)
    if not 'session_key' not in data:
        return jsonify(msg="获取用户信息失败"), 500

    # 根据session_key，调用微信工具，获取用户信息
    session_key = data['session_key']
    user_info = wxauth.get_user_info(encrypt_data, iv, session_key)

    if 'openId' not in user_info:
        return jsonify(msg="获取用户信息失败", user_info=user_info), 403
    # 把获取到用户数据保存到数据
    # 用是户否在数据库存在，如果存在更新原有的数据，不存在则保存到数据库
    user = User.query.filter_by(openId=user_info['openId']).first()
    if not user:
        user = User(user_info)
        db.session.add(user)
        db.session.commit()
    else:
        user.update_info(user_info)
        db.session.commit()
    # 生成token值
    token = _generate_jwt_token(user.id)
    data = {
        "msg": "success!",
        "token": token,
        "userInfo": {
            "uid": user.id,
            "gender": user.gender,
            "avatarUrl": user.avatarUrl,
            "country": user.country
        },
        "config": {
            "preference": user.preference,
            "brightness": user.brightness,
            "fontSize": user.fontSize,
            "background": user.background,
            "turn": user.turn
        }
    }

    return jsonify(data)

# 添加测试用户，只是用于测试功能展示所用
@user_bp.route('/add_user', methods=['POST'])
def add_user():
    # 添加用户，用来测试数据
    # 构造用户信息
    data = dict(
        openId='1' * 28,
        nickName="测试用户01",
        gender=0,
        city="北京",
        province="北京",
        country="中国",
        avatarUrl=""

    )
    # 把模拟的用户数据，通过模型类添加到数据库中。
    user = User(data)
    db.session.add(user)
    db.session.commit()

    #返回结果
    ret_data = {
        'msg':'添加成功',
        'user_id': user.id
    }
    return jsonify(ret_data)
# 获取用户信息
# 在请求视图之前就执行，检查是否有user_id

@user_bp.route('/get_user')
def get_userinfo():
    """
    1.默认的请求格式是get
    2.以用户id来测试，查询字符串
    3.生成token,返回token
    4.返回基本信息
    :return:
    """
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify(msg="用户不存在")
    token = _generate_jwt_token(user.id)
    ret_data = {
        "msg": "success!",
        "token": token,
        "userInfo": {
            "openId":user.openId,
            "uid": user.id,
            "gender": user.gender,
            "avatarUrl": user.avatarUrl,
            "country": user.country
        },
        "config": {
            "preference": user.preference,
            "brightness": user.brightness,
            "fontSize": user.fontSize,
            "background": user.background,
            "turn": user.turn
        }
    }
    return jsonify(ret_data)
