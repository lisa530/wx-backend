from flask import Blueprint,request,current_app,jsonify,g
from datetime import datetime

from models import Book,BookChapters,BookChapterContent,ReadRate

# 创建蓝图对象
book_bp = Blueprint('book',__name__,url_prefix='/book')


@book_bp.route('/chapters/<int:book_id>')
def chapter_list(book_id):
    """小说目录列表"""
    # 1.获取查询字符串参数,page,pagesize,order
    page = request.args.get('page',1,int) # 当前页
    pagesize = request.args.get('pagesize',10,int) # 一页显示多少条数据
    order = request.args.get('order',0,int) # 排序
    # 2.根据书籍id，查询书籍表
    book = Book.query.get(book_id)
    if not book:
        return jsonify(msg='查询的书籍不存在'),404
    # 3. 查询书籍章节目录表,条件为：按书籍id进行过滤查询
    query = BookChapters.query.filter(BookChapters.book_id==book_id)
    # 4. 根据order参数排序要件,如果为1表示倒序排序，如果为0表示升序排序
    if order == 1:
        query = query.order_by(BookChapters.chapter_id.desc())
    else:
        query = query.order_by(BookChapters.chapter_id.asc())
    # 5.对排序结果进行分页处理
    paginate = query.paginate(page,pagesize,False)
    data_list = paginate.items # 获取分页后的数据
    # 6. 遍历分页后的数据,获取章节信息
    items = []
    for data in data_list:
        items.append({
            'id':data.chapter_id, # 章节id
            'title': data.chapter_name, # 章节名称
        })
    # 7. 构造响应数据
    chapter_data = {
        'counts':paginate.total, # 分页后数据的总条数
        'page':paginate.page, # 当前页
        'pages':paginate.pages, # 总页数
        'items':items # 分页后的列表数据
    }
    # 8.转成json返回
    return jsonify(chapter_data)


@book_bp.route("/reader/<int:book_id>")
def reader_book(book_id):
    """小说阅读实现"""
    # 1.根据书籍id查询书籍表
    book = Book.query.get(book_id)
    # 判断书籍是否存在
    if not book:
        return jsonify(msg='查询的书籍不存在')
    # 2. 获取chapter_id查询参数,并校验参数是否小于1
    chapter_id = request.args.get('chapter_id',-1,int)
    if chapter_id < 1:
        return jsonify(msg='章节id不能小于1'),400
    # 3.根据章节id,查询书籍章节表
    chapter = BookChapters.query.get(chapter_id)
    # 4. 判断章节id是否有效
    if not chapter:
        return jsonify(msg='章节不存在'),404
    # 5. 如果章节数据存在，则查询书籍内容表
    # 根据书籍id和章节id过滤查询
    content = BookChapterContent.query.filter_by(book_id=book_id,chapter_id=chapter_id).first()
    # 6.如果用户登录,查询用户阅读进度表.
    progress = None # 默认为None
    if g.user_id: # 根据用户id book_id chapter_id过滤查询
        progress = ReadRate.query.filter_by(user_id=g.user_id,book_id=book_id,chapter_id=chapter_id)

    # 6.构造响应数据
    data = {
        'id':book_id, # 书籍id
        'title':book.book_name, # 书籍名称
        'chapter_id':chapter_id, # 章节id
        'chpter_name':chapter.chapter_name, # 章节名称
        'progress': progress.rate if progress else 0, # 阅读进度
        'atricle_content':content.content if content else '' # 章节内容
    }
    # 7. 返回结果
    return jsonify(data)