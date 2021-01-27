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
    """获取书架列表"""
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


@login_required
@my_books_bp.route("/<book_id>",methods=['POST'])
def add_book(book_id):
    """添加书籍"""
    # 1.添加登录验证装饰器
    user_id = g.user_id
    # 2.接收书籍id
    # 3.根据书籍id查询书籍列表
    # book = Book.query.filter(Book.book_id==book_id).first()
    book = Book.query.filter_by(book_id=book_id).first()
    # 书籍不存在提示错误信息
    if not book:
        return jsonify(msg='书籍不存在'),404
    # 查询书架表中是否有该书籍数据
    # book_shelf =BookShelf.query.filter(BookShelf.user_id==user_id,BookShelf.book_id==book_id).first()
    book_shelf = BookShelf.query.filter_by(user_id=user_id,book_id=book_id).first()
    # 如果书架没有书籍数据，添加书籍到书架中
    if not book_shelf:
        bk_shelf = BookShelf(user_id=user_id,book_id=book_id,book_name=book.book_name,cover=book.cover)
        # 提交到数据库
        db.session.add(bk_shelf)
        db.session.commit()
        # 返回添加成功的信息
        return jsonify(msg='添加书籍到书架成功')

    # 书籍中该书籍已存在，则提示信息
    return jsonify(msg='书架中该书籍已在存在'),404


@login_required
@my_books_bp.route("/<book_id>", methods=['DELETE'])
def del_book(book_id):
    """删除书籍"""
    # 1.添加登录装饰器，获取用户信息
    user_id = g.user_id
    # 2. 查询书架中要删除的书籍：
    # 使用 user_id和 书籍id作为查询条件
    bk_shelf = BookShelf.query.filter_by(user_id=user_id,book_id=book_id).first()
    # 3. 如果删除的书籍不在书架中则提示
    if not bk_shelf:
        return jsonify(msg='该书籍在书架中不存在'),404
    # 4. 存在，则删除并提交到数据库
    db.session.delete(bk_shelf)
    db.session.commit()
    # 5. 返回删除后的信息
    return jsonify(msg='删除书籍成功')







