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