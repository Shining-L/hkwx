import base64
import json
from flask import Blueprint, request, jsonify
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from utils import jwt_utils
from models import User, db

user_bp = Blueprint('users', __name__, url_prefix="/user")

# 设置微信服务器的接口
WECHAT_API_URL = "https://api.weixin.qq.com/sns/jscode2session"

# 设置appID
APP_ID = 'wxead114070c96c908'

# 设置APP密钥
APP_SECRET = "e24372ff91bce62df9572726f72a6051"


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

    # 向微信服务器发起请求,进行登陆凭证校验，换取openid和session_key
    params = {
        "appid": APP_ID,
        "secret": APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }
    """
    {"session_key":"z4T/xQcXAeUCALcIqQ/fGw==","openid":"oBae75GTRzscqR-j4JT9oOE8ejCk"}
    """
    response = requests.get(WECHAT_API_URL, params=params)
    wechat_response = json.loads(response.text)
    # 对加密的数据进行解密
    session_key = wechat_response.get("session_key")
    openid = wechat_response.get("openid")

    if not session_key or not openid:
        return jsonify(msg="获取用户信息失败"), 500

    # 解密数据
    iv_decode = base64.b64decode(iv)
    session_key_decode = base64.b64decode(session_key)
    encrypt_data_decode = base64.b64decode(encrypt_data)

    cipher = AES.new(session_key_decode, AES.MODE_CBC, iv_decode)
    decrypted_data_json = unpad(cipher.decrypt(encrypt_data_decode), AES.block_size)

    # 转换解密后的数据，确保数据是字典格式
    decrypted_data = json.loads(decrypted_data_json)

    # 把获取到用户数据保存到数据
    # 用是户否在数据库存在，如果存在更新原有的数据，不存在则保存到数据库
    user = User.query.filter_by(openId=openid).first()
    if not user:
        user = User(decrypted_data)
        db.session.add(user)
        db.session.commit()
    else:
        user.update_info(decrypted_data)
        db.session.commit()
    # 生成token值
    token = jwt_utils.generate_jwt(payload={'user_id': user.id}, expire=6000)
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
