from flask import Flask


# 封装程序实例：根据传入参数的不同，创建不同的app
def create_applet_app(config_name=None):
    """定义工厂函数"""
    app = Flask(__name__)

    # 导入蓝图对象
    from .user import user_bp
    # 注册蓝图
    app.register_blueprint(user_bp)
    from .my_books import my_books_bp
    app.register_blueprint(my_books_bp)
    from .category import category_bp
    app.register_blueprint(category_bp)
    from .search import search_bp
    app.register_blueprint(search_bp)
    from .recommend import recommend_bp
    app.register_blueprint(recommend_bp)
    from .book import book_bp
    app.register_blueprint(book_bp)
    from .my_history import my_history_bp
    app.register_blueprint(my_history_bp)
    from .reader_config import config_bp
    app.register_blueprint(config_bp)

    # 从models文件夹中导入sqlalchemy对象
    from models import db
    # 将app和db对象进行绑定
    db.init_app(app)
    # 获取配置信息
    app.config.from_object(config_name)
    # 导入请求钩子，用户的权限校验
    from lib.middlewares import before_request
    # 相当于@app.before_request
    app.before_request(before_request)

    return app