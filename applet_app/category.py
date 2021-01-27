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
