from flask import request, g
from .jwt_utils import verify_jwt

"""
Authorization(授权)指的是控制对系统中资源访问的过程，确定用户做什么？
"""
def before_request():
    g.user_id = None
    auth = request.headers.get("Authorization")
    if auth:
        payload = verify_jwt(token=auth)
        if payload:
            g.user_id = payload.get('user_id')
