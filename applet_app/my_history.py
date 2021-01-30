from flask import Blueprint,request,g,current_app,jsonify

# 导入登录装饰器
from lib.decoraters import login_required
# 导入模型类
from models import BrowseHistory,db

# 创建蓝图对象
my_history_bp = Blueprint('my_history',__name__,url_prefix='/my')


@login_required
@my_history_bp.route('/histories')
def my_history():
    """我的浏览记录"""
    # 1.获取参数,page和pagesize
    page = request.args.get('page',1,int)
    pagesize = request.args.get('pagesize',10,int)
    # 2. 查询用户浏览记录表,根据user_id查询，并进行分页处理
    brower_data = BrowseHistory.query.filter_by(user_id=g.user_id)
    paginate = brower_data.paginate(page,pagesize,False)
    # 3. 获取分页后的数据
    history_data = paginate.items # 获取分页后的列表
    items = []
    # 4. 遍历浏览记录，获取书籍表的信息
    for item in history_data:
        items.append({
            'id':item.book.book_id, # 通过关系引用(book)获取用户的书籍
            'title':item.book.book_name,
            'author':item.book.author_name,
            'status':item.book.status,
            'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],item.book.cover),
            'lastTime':item.updated.strftime('%Y-%m-%d %H:%M:%S') # 修改时间，转成python标准日期格式
        })
    # 5.构造字典数据结构
    data = {
        'counts':paginate.total, # 一页数据总条数
        'pagesize':pagesize, # 一页显示多少条数据
        'pages':paginate.pages, # 总页数
        'page':paginate.page, # 当前所在页
        'items':items # 书籍列表
    }
    # 6. 转成json返回
    return jsonify(data)


@login_required
@my_history_bp.route('/histories',methods=['DELETE'])
def delete_history():
    """清除浏览记录"""
    # 1.查询用户浏览记录表，根据用户id过滤查询
    history_data = BrowseHistory.query.filter_by(user_id=g.user_id).all()
    # 2. 遍历用户浏览记录，删除浏览记录并提交到数据库
    for history in history_data:
        db.session.delete(history)
    db.session.commit()
    # 3. 返回结果
    return jsonify(msg='删除成功')

