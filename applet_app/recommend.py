from flask import Blueprint,current_app,jsonify

from models import BookBigCategory,Book

# 创建蓝图对象
recommend_bp = Blueprint('recommend',__name__,url_prefix='/recommend')


@recommend_bp.route("/hots/<int:category_id>")
def recommends(category_id):
    """同类热门数据推荐"""
    # 1. 查询分类id查询一级分类表
    pareng_category = BookBigCategory.query.get(category_id)
    books = [] # 用于存储最终要返回的书籍数据
    # 2. 判断一级分类是否存在
    if pareng_category:
        # 通过一级分类查询二级分类数据
        subs_id = [i.cate_id for i in pareng_category.second_cates] # 关系字段查询
        # 3. 查询书籍表，条件为：查询分类id在二级分类id范围内，默认取4条
        book_list = Book.query.filter(Book.cate_id.in_(subs_id)).limit(4)

        # 4. 遍历每一本书籍信息
        for book in book_list:
            books.append({
                'id':book.book_id,
                'title':book.book_name,
                'intro':book.intro,
                'author':book.author_name,
                'state':book.status,
                'category_id':book.cate_id,
                'category_name':book.cate_name,
                'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],book.cover)
            })
    # 5. 如果没有一级分类数据,默认返回4条数据
    book_list = Book.query.limit(4)
    # 6遍历书籍对象，获取每一本书籍信息
    for book in book_list:
        books.append({
            'id':book.book_id,
            'title':book.book_name,
            'intro':book.intro,
            'author':book.author_name,
            'state':book.status,
            'category_id':book.cate_id,
            'category_name':book.cate_name,
            'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'], book.cover)
        })

    # 7.转成json格式，返回书籍列表数据
    return jsonify(books)

