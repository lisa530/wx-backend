from flask import Flask
# 数据库配置
from flask_sqlalchemy import SQLAlchemy
# 脚本管理器
from flask_script import Manager
# 数据库迁移
from flask_migrate import Migrate,MigrateCommand


app = Flask(__name__)
# 配置数据库连接信息
SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/wenxue'
# 动态追踪修改信息，不设置会提示警告信息，设置True或False都可以关闭警告信息。
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 实例化sqlaclchemy对象,将app绑定到db对象上
db = SQLAlchemy(app)

# 实例化脚本管理器对象
manager = Manager(app)

# 使用迁移框架migrate
Migrate(app,db)
# 添加迁移命令,接收两个参数,db,MigrateCommand
manager.add_command('db',MigrateCommand) # 这个'db'和数据库db对象不是同一个，只是一个字符串的名字

@app.route('/')
def index():
    return "hello lisa"


if __name__ == '__main__':
    # app.run()
    # 使用manager.run代替app.run()
    manager.run()