from flask import Blueprint,request,jsonify

from models import SearchKeyWord

search_bp = Blueprint('search',__name__,url_prefix='/search')


@search_bp.route("/tags")
def tag_list():
    """热门搜索词实现"""
    # 1.接收查询参数key_word
    key_word = request.args.get('key_word')
    # 2. 判断key_word是否有效
    if not key_word:
        return jsonify([])
    # 3. 查询关键词表,查询条件为：搜索的key_word包含在模型类的keyword字段中，并限制展示10条数据
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

