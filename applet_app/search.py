from flask import Blueprint,request,jsonify,current_app
from sqlalchemy import not_

from models import SearchKeyWord, Book, db

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


@search_bp.route('/recommends')
def recommends():
    """精确/模糊/推荐/实现"""
    # 1.接收查询参数
    key_word = request.args.get('key_word')
    # 2.查询SearchKeyWord表,根据key_word查询
    skw = SearchKeyWord.query.filter(SearchKeyWord.keyword==key_word).first()
    # 3. 判断搜索关键词是否存在
    if skw is None:
        # 如果不存在，将key_word和count保存到数据表中
        skw = SearchKeyWord.query.filter_by(keyword=key_word,count=0)

    # 4. 存在则count计数加1,如果count大于10, 将is_hot标记为热门关键词
    skw.count += 1
    if skw.count >= 10:
        skw.is_hot = True
    db.session.add(skw)
    db.session.commit()
    # 4.定义空列表：用来存储7条书籍数据的id,进行书籍数据重复的判断
    book_list = []
    # 精确匹配1条：查询书籍表,查询条件为：key_word和书籍表book_name匹配的值
    accurate_data = Book.query.filter_by(book_name=key_word).first()
    # 5.定义字典：用来存储匹配到的的书籍数据
    accurate_dict = {}
    # 如果书籍中匹配到关键字
    if accurate_data:
        accurate_dict = {
            'id':accurate_data.book_id,
            'title':accurate_data.book_name,
            'intro':accurate_data.intro,
            'state':accurate_data.status,
            'catetory_id':accurate_data.cate_id,
            'category_name':accurate_data.cate_name,
            'imgURL':'http://{}/{}'.format(['QINIU_SETTINGS']['host'],accurate_data.cover)
        }
        book_list.append(accurate_data.book_id)

    # 6.模糊匹配2条：
    # 查询条件为：书名包含查询关键词(key_word) 并且 该书籍的id不是精确查询的数据，默认提取2条
    query = Book.query.filter(Book.book_name.contains(key_word),not_(Book.book_id.in_(book_list))).limit(2)
    # match_data = query.limit(2)
    match = [] # 定义模糊匹配列表，用于存储模糊匹配后的书籍
    # 遍历模糊匹配书籍对象,将每一本模糊匹配的书籍数据追加列列表中
    for book in query:
        match.append({
            'id':book.book_id,
            'title':book.book_name,
            'intro':book.intro,
            'state':book.status,
            'category_id':book.cate_id,
            'category_name':book.cate_name,
            'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],book.cover)
        })
        book_list.append(book.book_id)

    # 7.推荐4条：根据书籍表：条件为：查询不在之前查询到数据范围内的书籍，取出4条作为推荐阅读。
    recommends_data = Book.query.filter(not_(Book.book_id.in_(book_list))).limit(4)
    recommends_list = [] # 定义推荐列表，用于存储推荐书籍数据
    # 遍历书籍对象,将每一本推荐的书籍进行追加到列表中
    for book in recommends_data:
        recommends_list.append({
            'id': book.book_id,
            'title': book.book_name,
            'intro': book.intro,
            'state': book.status,
            'category_id': book.cate_id,
            'category_name': book.cate_name,
            'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'], book.cover)
        })
    # 构造字典，返回结果：精确匹配1条、模糊匹配2条、推荐4条，共7条书籍数据。
    data = {
        'accurate':accurate_data, # 精确匹配
        'match':match, # 模糊匹配
        'recommends_list':recommends_list # 推荐的书籍
    }

    return jsonify(data)



