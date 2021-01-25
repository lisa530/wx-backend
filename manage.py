
# 数据库配置
from flask_sqlalchemy import SQLAlchemy
# 脚本管理器
from flask_script import Manager
# 数据库迁移
from flask_migrate import Migrate,MigrateCommand
# 导入工厂函数
from applet_app import create_applet_app
# 导入配置信息的字典
from config import config_dict

# 实例化工厂函数
app = create_applet_app(config_dict['dev_config'])

# 实例化sqlaclchemy对象,将app绑定到db对象上
db = SQLAlchemy(app)


# 实例化脚本管理器对象
manager = Manager(app)

# 使用迁移框架migrate
Migrate(app,db)
# 添加迁移命令,接收两个参数,db,MigrateCommand
manager.add_command('db',MigrateCommand) # 这个'db'和数据库db对象不是同一个，只是一个字符串的名字


if __name__ == '__main__':
    # app.run()
    # 查看路由映射
    print(app.url_map)
    # 使用manager.run代替app.run()
    manager.run()