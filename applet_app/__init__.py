from flask import Flask


# 封装程序实例：根据传入参数的不同，创建不同的app
def create_applet_app(config_name=None):
    """定义工厂函数"""
    app = Flask(__name__)

    # 获取配置信息
    app.config.from_object(config_name)
    return app