from flask import Blueprint,request,jsonify,current_app

from models import SearchKeyWord,Book

search_bp = Blueprint('search',__name__,url_prefix='/search')


@search_bp.route("/tags")
def tag_list():
    """热门搜索词实现"""
    # 1.接收查询参数key_word
    key_word = request.args.get('key_word')
    # 2. 判断key_word是否有效
    if not key_word:
        return jsonify([])
    # 3. 查询关键词表,查询条件为：搜索的key_word包含在模型类的keyword字段中，默认返回10条数据
    search_list = SearchKeyWord.query.filter(SearchKeyWord.keyword.concat(key_word)).limit(10)
    # 4.构造字典，将遍历后的查询对象放至字典中
    # data = []
    # # 遍历对象
    # for search in search_list:
    #     # 每遍历一次将对象的字段进行赋值
    #     index = {
    #         'title':search.keyword,
    #         'isHOt':search.is_hot
    #     }
    #     # 追加到列表中
    #     data.append(index)

    data = [{
        'title':index.keyword, # 热门搜索关键词
        'isHot':index.is_hot # 是否为热点
    }for index in search_list] # 使用列表推导式遍历search_list对象

    return jsonify(data)


@search_bp.route('/books')
def search_books():
    """搜索书籍列表"""
    # 1.接收查询参数
    key_word = request.args.get('key_word') # 搜索关键词
    page = request.args.get('page',1,int)  # 当前所在页
    pagesize = request.args.get('pagesize',10,int) # 一页显示多少条数据
    # 校验关键词参数
    if not key_word:
        return jsonify(msg='参数无效'),400
    # 2. 查询书籍表，，条件为：查询书籍名称中包含key_word关键字
    query = Book.query.filter(Book.book_name.contains(key_word))
    # 3. 对查询结果进行分页处理
    paginate = query.paginate(page,pagesize,False) # 接收三个参数，当前页，一页显示多少条数据，分页异常不报错
    # 4. 获取分页后的数据
    book_list = paginate.items # 得到分页后的数据
    # 5.遍历分页后的数据，获取每本书籍数据
    items = []
    for book in book_list:
        items.append({
            'id':book.book_id,
            'title':book.book_name, # 书籍名称
            'intro':book.intro, # 简介
            'state':book.status, # 状态
            'category_id':book.cate_id, # 分类id
            'category_name':book.cate_name, # 分类名称
            # 书籍封面图片地址
            'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],book.cover)
        })
    # 6.构造字典，返回结果
    data = {
        'counts':paginate.total, # 总条数
        'pages': paginate.pages, # 总页数
        'page': paginate.page, # 当前页
        'items':items # 分页后数据
    }

    return jsonify(data)

