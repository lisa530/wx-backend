from flask import Blueprint,request,jsonify,g

from models import User,db
# 导入登录装饰器
from lib.decoraters import login_required

# 创建蓝图对象
config_bp = Blueprint('config',__name__,url_prefix='/config')


@login_required
@config_bp.route("/preference",methods=['POST'])
def preference():
    """阅读偏好设置"""
    # 1. 从请求体中获取参数
    gender = request.json.get('gender')
    gender = int(gender)
    # 2. 校验性别的范围
    if gender not in [0,1]: # 1表示 男 0表示 女
        return jsonify(msg='性别参数错误')
    # 3. 查询用户表,根据user_id进行过滤查询
    user = User.query.filter_by(id=g.user_id).first()
    # User.query.filter_by(id=g.user_id).update({'gender':gender})
    # db.session.commit()
    # 4. 保存用户数据
    user.gender = gender # 将用户设置的gender绑定到user表中
    db.session.add(user)
    db.session.commit()
    # 5.返回结果
    return jsonify(msg='设置成功')


@login_required
@config_bp.route('/reader',methods=['POST'])
def reader_config():
    # 1.获取参数、亮度、字号、背景、翻页效果
    brightness = request.json.get('brightness') # 亮度
    fontsize = request.json.get('fontsize') # 文字大小
    background = request.json.get('background') # B1 ~ B6 内置背景
    turn = request.json.get('turn') # T1 仿真 T2 平滑 T3 无 翻页模式
    # 2. 查询用户表,根据用户id查询用户信息
    user = User.query.get(g.user_id)
    # 3. 保存设置信息
    if brightness:
        user.brightness = brightness
    if fontsize:
        user.fontSize = fontsize
    if background:
        user.background = background
    if turn:
        user.turn = turn
    db.session.add(user)
    db.session.commit()
    # 返回结果
    return jsonify(msg='设置成功')