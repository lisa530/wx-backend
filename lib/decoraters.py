from flask import g,jsonify
import functools


def login_required(func):
    """登录验证装饰器"""

    # 作用：让被装饰器的装饰的函数的属性(函数名)不发生变化。
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        # 1.判断用户id是否存在,不存在则从g对象中获取用户id
        if not g.user_id:
            return jsonify(msg='token error'),401
        return func(*args,**kwargs)
    # 让被装饰器的装饰的函数的属性(函数名)不发生变化。
    # wrapper.__name__ = func.__name__
    return wrapper