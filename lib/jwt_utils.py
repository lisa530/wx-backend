import jwt
from flask import current_app


def generate_jwt(payload,expire,secret_key=None):
    """
    封装生成jwt工具
    :param payload:存储用户的信息
    :param expire 过期时间
    :param secret_key 密钥
    """
    #  _payload表示私有属性,存储用户信息过期时间
    _payload = {'exp':expire}
    _payload.update(payload)
    # 验证密钥是否过期
    if not secret_key:
        # 从flask对象config属性中获取SECRET_KEY
        secret_key = current_app.config['SECRET_KEY']

    # 生成jwt_token
    # 接收三个参数：_payload：存储用户有效信息,secret_key密钥，algorithm:指定加密方式
    token = jwt.encode(_payload,secret_key,algorithm='HS256')
    # 返回解码后的token
    return token.decode()


def verify_jwt(token,secret_key=None):
    """封装校验jwt工具"""
    if not secret_key: # secret_key不存在
        secret_key = current_app.config.get('SECRET_KEY')

    try:
        payload = jwt.decode(token,secret_key,algorithms=['HS256'])
    except jwt.PyJWTError:
        payload = None
    return payload


