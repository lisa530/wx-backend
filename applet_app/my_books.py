# 导入随机数
import random
# 导入蓝图对象
from flask import Blueprint,g,current_app,jsonify
# 导入登录验证装饰器
from lib.decoraters import login_required
# 导入书架模型类
from models import Book,BookShelf,db,User

# 创建蓝图对象
my_books_bp = Blueprint('mybook',__name__,url_prefix='/mybooks')

# 定义路由
@login_required
@my_books_bp.route('/') # 使用蓝图绑定路由
def mybooks_list():
    # 1.从g对象中获取用户id
    user_id = g.user_id
    # 2.查询书架中的所有书籍，按创建时间倒序排序
    mybooks = BookShelf.query.filter_by(user_id=user_id).order_by(BookShelf.created.desc()).all()
    # 定义临时列表，存储数据
    data = []
    # 3. 判断书架是否有数据
    if not mybooks:
        # 书架中没有书籍数据，从数据库中查询所有书籍，随机挑选5本书，存入书架中
        books = Book.query.all()
        books_list = random.sample(books,5)
        # 4.遍历书籍列表对象
        for bk in books_list:
            # 每遍历一次随机获取每一本书的信息
            book_shelf = BookShelf(
                user_id=user_id,
                book_id=bk.book_id,
                book_name=bk.book_name,
                cover=bk.cover
            )
            # 5.提交到数据库
            db.session.add(book_shelf)
            # 6.添加七牛云存储的图片绝对路径
            data.append({
                'id':bk.book_id, #
                'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],bk.cover),
                'title':bk.book_name # 书名
            })
        db.session.commit()
        # 7.将对象换为json返回
        return jsonify(data)

    else: # 书架中有书籍数据，遍历书籍数据，获取每本书的数据
        for bk in mybooks:
            data.append({
                'id':bk.book_id,
                'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'], bk.cover),
                'title': bk.book_name
            })
        return jsonify(data)





