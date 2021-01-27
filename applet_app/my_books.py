# 导入随机数
import random
# 导入蓝图对象
from flask import Blueprint,g,current_app,jsonify
# 导入登录验证装饰器
from lib.decoraters import login_required
# 导入书架模型类
from models import Book,BookShelf,db,User,BookChapters,ReadRate

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


@login_required
@my_books_bp.route("/last")
def book_last_reading():
    """获取最后阅读的书籍"""
    # 1.从g对象中获取用户信息
    user_id = g.user_id
    # 2. 查询用户是否存在
    user = User.query.get(user_id)
    read_rate = None # 阅读进度默认为None
    # 3. 判断用户是否阅读书籍
    if not user.last_read:
        # 用户没有阅读，默认查询书籍表的第一本书籍 作为用户阅读的书籍
        book = Book.query.first()
        # 将用户阅读的书籍id绑定到user对象中的last_read属性中
        user.last_read = book.book_id
        # 查询该书籍的章节信息，按章节id升序排序
        bk_chapter = BookChapters.query.filter_by(book_id=book.book_id).order_by(BookChapters.chapter_id.asc()).first()
        #  将阅读书籍的章节id保存到用户表中last_read_chapter_id中
        user.last_read_chapter_id = bk_chapter.chapter_id
        # 将查询结果保存到阅读进度表中
        read_rate = ReadRate(
            user_id=user_id, # 用户id
            book_id = book.book_id, # 书籍id
            chapter_id=bk_chapter.chapter_id, # 章节id
            chapter_name=bk_chapter.chapter_name # 章节名称
        )
        # 4.保存数据，不仅要保存用户表也要保存阅读进度表
        # db.session.add(read_rate)
        # db.session.add(user)
        db.session.add_all([read_rate,user])
        db.session.commit()
    else:
        # 5. 用户已阅读过书籍，查询用户最后阅读的书籍信息
        book = Book.query.get(user.last_read)
        # 如果用户没有阅读进度，查询阅读进度表，返回第一章的信息
    if not read_rate:
        read_rate = ReadRate.query.filter_by(
            user_id=user.id, # 用户id
            book_id = book.book_id, # 书籍id
            chapter_id=user.last_read_chapter_id # 最后阅读的章节id
        ).first()

    # 7.构造字典
    data ={
        'id':book.book_id,
        'title':book.book_name, # 书籍名称
        'chapter':read_rate.chapter_name, # 最后阅读章节名称
        'progress': read_rate.rate, # 阅读进度
        # 书籍封面图片地址
        'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],book.cover)
    }
    # 转成json格式返回
    return jsonify(data)










