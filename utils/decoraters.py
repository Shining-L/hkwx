from flask import g, jsonify
import functools



# functools.wraps(func)装饰wrapper函数，保留被装饰函数的元信息，比如：函数的名称，文档字符串，使用装饰器更加透明
def login_required(fun):
    @functools.wraps(fun)  # 让被装饰器的装饰的函数的属性(函数名)不会发生变化
    def wrapper(*args, **kwargs):
        if not g.user_id:
            return jsonify(msg="token 异常"), 401
        return fun(*args, **kwargs)

    return wrapper

