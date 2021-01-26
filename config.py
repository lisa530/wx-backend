# # 配置数据库连接信息
# app.config['SQLALCHEMY_DATABASE_URI']= 'mysql://root:123456@localhost/wenxue'
# # 动态追踪修改信息，不设置会提示警告信息，设置True或False都可以关闭警告信息。
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class BaseConfig(object):
    """封装配置类"""
    SECRET_KEY = 'QRDFJIRE-PPJRERR12334'
    # jwt_token过期时间
    JWT_EXPIRE_TIME = 24

    DEBUG = None
    # 配置数据库连接信息
    SQLALCHEMY_DATABASE_URI= 'mysql://root:123456@localhost/wenxue'
    # 动态追踪修改信息，不设置会提示警告信息，设置True或False都可以关闭警告信息。
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 七牛云配置信息
    QINIU_SETTINGS = {
        'access_key': '51DGWfSzbBws6szT3GVoZ8nMuqVVFAFV2P_StMbr',
        'secret_key': 'pAo3kBotA7PQLCuIF9Y2wCc7AfRs0MEss2-qdTbb',
        'bucket_name': 'hmwx01',
        'host': 'pu3lpnbqt.bkt.clouddn.com',
    }

class DevelopmentConfig(BaseConfig):
    """开发配置类"""
    DEBUT = True
    pass


class ProductionConfig(BaseConfig):
    """生产配置类"""
    DEBUG = False
    pass


# 定义字典，实现不同配置类的映射
config_dict = {
    'base_config': BaseConfig,
    'dev_config': DevelopmentConfig,
    'pro_config': ProductionConfig
}


