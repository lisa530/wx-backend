from flask import Blueprint,request, jsonify,current_app
# 导入微信工具
from lib.wxauth import get_wxapp_session_key,get_user_info

# 导入数据库sqlaclchemy
from models import db
# 导入模型类
from models import User
# 导入日期模块
from datetime import datetime,timedelta
# 导入jwt工具
from lib.jwt_utils import generate_jwt

# 创建蓝图对象
user_bp = Blueprint('user_bp', __name__,url_prefix='/users')


def _generate_jwt_token(user_id):
    """
    生成jwt_token
    :param: user_id: 表示生成token的载荷中存储的用户信息
    """
    # 1.生成当前时间
    now = datetime.utcnow()
    # 2.根据时间差，指定token的过期时间
    # expire = now + timedelta(hours=24)
    expire = now + timedelta(hours=current_app.config.get("JWT_EXPIRE_TIME"))
    # 3. 调用jwt工具，传入两个参数,当前登录的用户user_id,token过期时间
    token = generate_jwt({'user_id':user_id,},expire=expire)
    # 4.返回token
    return token

@user_bp.route('/login',methods=['POST'])
def login():
    """第三方登录"""
    # 1.接收前端传递的参数,code（用户登录凭证，有效期5分钟)
    # 使用 code 换取 openid 和 session_key 等信息
    code = request.json.get('code','')
    # iv(加密算法初始量)
    iv = request.json.get('iv','')
    #  encryptedData 包括敏感数据在内的完整用户信息的加密数据
    envryptedData = request.json.get('envryptedData','')

    # 2.判断参数是否存在
    if not iv or not envryptedData or not code:
        return jsonify(msg='参数错误'),403
    # 3.调用微信工具，根据code获取session_key
    data = get_wxapp_session_key(code)
    # 判断session_key是否存在
    if 'session_key' not in data:
        return jsonify(msg='获取session_key信息失败',data=data),500
    # 4.根据session_key调用微信工具，获取用户信息
    session_key = data['session_key']
    user_info = get_user_info(envryptedData, iv, session_key)

    # 判断用户是否获取到openid
    if 'openId' not in user_info:
        return jsonify(msg='获取用户信息失败',user_info=user_info),403
    # 5.保存用户数据
    openid = user_info['openId']
    user = User.query.filter_by(openId=openid).first()
    if not user:
        user = User(user_info)
        db.session.add(user)
        db.session.flush()
    else:
        user.update_info(user_info)
        db.session.commit()

    # 6.调用jwt工具，生成token
    token = _generate_jwt_token(user.id)
    # 7.构造字典
    ret_data = {
        'token':token,
        'user_info':{  # 用户对象
            'uid':user.id,
            'gender':user.gender,
            'avatarUrl':user.avatarUrl # 头像
        },
        "config":{  # 用户阅读配置
            "preference": user.preference,
            "brightness": user.brightness,
            "fontSize": user.fontSize,
            "background": user.background,
            "turn": user.turn
        }
    }
    # 返回json数据对象
    return jsonify(ret_data)


@user_bp.route("/temp_add_user",methods=['POST'])
def temp_add_user():
    """添加测试用户功能"""
    # 1. 构造用户对象
    data = dict(
        openId = '1'*32,
        nickName = '测试用户001',
        gender = 1,
        city = '广州市',
        province = '广东省',
        country = '中国',
        avatarUrl = 'default'
    )
    # 模拟添加用户数据，通过模型类添加到数据库中
    user = User(data)
    db.session.add(user)
    db.session.commit()
    # 返回添加成功后的用户结果
    ret_data = {
        'msg':'添加用户成功',
        'user_id':user.id
    }
    # 3. 返回json数据
    return jsonify(ret_data)








