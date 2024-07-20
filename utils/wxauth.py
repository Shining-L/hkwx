import requests
from .WXBizDataCrypt import WXBizDataCrypt

# 设置微信服务器的接口
WECHAT_API_URL = "https://api.weixin.qq.com/sns/jscode2session"

# 设置appID
APP_ID = 'wxead114070c96c908'

# 设置APP密钥
APP_SECRET = "e24372ff91bce62df9572726f72a6051"


def get_wxapp_session_key(code):
    params = {
        "appid": APP_ID,
        "secret": APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }
    try:
        response = requests.get(WECHAT_API_URL, params=params)
        response.raise_for_status() # 检查请求是否成功
        data = response.json()
        print(data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"请求失败:{e}")
        return None

def get_user_info(encrypt_data, iv, session_key):
    pc = WXBizDataCrypt(APP_ID, session_key)
    return pc.decrypt(encrypt_data, iv)
