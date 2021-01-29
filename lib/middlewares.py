from flask import request,g
from .jwt_utils import verify_jwt


def before_request():
    """
    登录用户校验中间件
    需求：有些接口必须要用户登录才能进入到视图，需要校验用户身份信息
    """
    g.user_id = None
    # 1.从前端请求头中获取Authorization参数
    auth = request.headers.get('Authorization')
    if auth:
        # 使用jwt工具校验token是否有效
        payload = verify_jwt(token=auth)
        # 从payload中提取用户id，并把用户id赋值给g对象
        if payload:
            g.user_id = payload.get("user_id")
