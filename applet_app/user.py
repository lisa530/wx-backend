from flask import Blueprint


# 创建蓝图对象
# user_bp = Blueprint('user_bp', __name__,url_prefix='/users')
user_bp = Blueprint('user_bp', __name__)

# 将蓝图绑定到路由
@user_bp.route("/")
# @app.route("/")
def index():
    return "hello lisa"


