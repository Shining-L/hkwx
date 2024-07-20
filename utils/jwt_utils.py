import jwt
from flask import current_app


# 生成
def generate_jwt(payload, expire, secret_key=None):
    """

    :param payload: 表示存储的用户信息
    :param expire: jwt的过期时间
    :param secret_key: 密钥
    :return:
    """
    _payload = {'exp': expire}
    _payload.update(payload)

    # 判断是否传入密钥
    if not secret_key:
        secret_key = current_app.config['SECRET_KEY']

    token = jwt.encode(_payload, secret_key, algorithm="HS256")
    return token


# 校验
def verify_jwt(token, secret_key=None):
    if not secret_key:
        secret_key = current_app.config.get('SECRET_KEY')

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    except jwt.PyJWTError:
        payload = None
        print(payload)
    return payload
