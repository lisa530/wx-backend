from flask import  Blueprint,request,current_app,jsonify

# 导入模型类
from models import BookBigCategory,Book


# 创建蓝图
category_bp = Blueprint('category_bp',__name__,url_prefix='/categories')


@category_bp.route('/')
def category_list():
    """分类列表"""
    # 1.接收查询字符串参数
    gender = request.args.get('gender',1,int)
    # 2. 根据性别查询所有一级分类数据, 1:男生, 2:女生
    parent_category = BookBigCategory.query.filter_by(channel=gender).all()
    cate_list = []

    # 3.遍历一级分类数据，将一级分类保存到字典中
    for book_category in parent_category:
        parent_dict = {
            'id':book_category.cate_id, # 一级分类id
            'title':book_category.cate_name, # 一级分类名称
            # 一级分类书籍封面图片地址
            'imgURL':'http://{}/{}'.format(current_app.config["QINIU_SETTINGS"]['host'],book_category.icon),
            'subCategory':[] # 二级分类
        }
        # 4.遍历一级分类下的二级分类，将分类信息保存到字典中
        for category in book_category.second_cates: # 通过外键查询
            temp = {
                'id':category.cate_id, # 二级分类id
                'title':category.cate_name, # 二级分尖名称
            }
            # 将二级分类作为值赋值给subCategory
            parent_dict['subCategory'].append(temp)
        # 将一级分类和二级分类追加到列表中
        cate_list.append(parent_dict)

    # 5.返回分类数据
    return jsonify(cate_list)


@category_bp.route('/filters')
def category_book_list():
    """
    获取分类书籍列表
    :param: page当前所在页
    :param: pagesize一页显示多少条
    :param:category_id分类id
    :param: worlds字数统计
    :param: order:排序
    :param: paginate分页器对象
    :param:pagesize属性:一页显示多少条数据
    :param: page属性: 当前页
    :param: pages属性:总页数
    :param: counts属性:分页后的总页数
    :param: items属性:获取分页后列表数据
    """
    # 1.接收查询参数
    page = request.args.get('page',1,int)
    pagesize = request.args.get('pagesize',10,int)
    category_id = request.args.get('category_id',0,int)
    # 字数类型说明：0表示所有，1表示50万字以下，2表示50~100万字，3表示100万字以上
    words = request.args.get('words',-1,int)
    # 排序条件说明：1表示按热度，2表示按收藏
    order = request.args.get('order',1,int)
    # 2. 判断分类是否存在
    if not category_id:
        return jsonify(msg='缺少分类id'),400
    # 3.根据分类id作为查询条件，获取一级分类数据
    categories = BookBigCategory.query.get(category_id)
    # 4.根据一级分类获取二级分类数据,通过关系引用获取二级分类
    # 使用set集合去重
    seconds_id = set([i.cate_id for i in categories.second_cates])
    # 5.查询书籍表,获取分类范围内的书籍数据
    # 保存的是查询结果对象
    query = Book.query.filter(Book.cate_id.in_(seconds_id))
    # 6.根据条件words参数查询书籍数据
    # 1表示50万字以下，2表示50~100万字，3表示100万字以上
    if words == 1:
        query = query.filter(Book.word_count < 500000)
    elif words == 2:
        query = query.filter(Book.word_count.between(500000,1000000))
    elif words == 3:
        query = query.filter(Book.word_count > 1000000)

    # 7.根据排序条件order，按照最热、收藏数量进行排序查询
    # 1表示热销度,2表示按收藏排序
    if order == 1:
        query = query.order_by(Book.heat.desc())
    elif order == 2:
        query = query.order_by(Book.collect_count.desc())
    else:
        return jsonify(msg='错误的排序参数'),400

    # 8.对查询结果进行分页
    # paginate() 方法的返回值是一个 Pagination 类对象
    # paginate接收三个参数：page当前页,pagesize一页显示多少条数据，False表示分页异常不报错
    paginate = query.paginate(page,pagesize,False)
    books_list = paginate.items # 分页后的数据
    items = []
    # 遍历分页数据,获取每页数据及总页数
    for item in books_list:
        items.append({
            'id':item.book_id, # 书籍id
            'title':item.book_name, # 书籍名称
            'category_id':item.cate_id, # 分类id
            'category_name':item.cate_name, # 分类名称
            'author':item.author_name, # 作者
            'state':item.status, # 连载状态
            'introduction':item.intro, # 简介
            'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],item.cover)
        })
    # 9.将分页数据构造成字典，转换为json数据返回
    json_data = {
        'counts': paginate.total,  # 分页后的数据总条数
        'pagesize': pagesize,  # 一页显示多少条数据
        'pages': paginate.pages, # 总页数
        'page': paginate.page, # 当前所在页
        'items': items # 获取分页后列表数据
    }
    return jsonify(json_data)


