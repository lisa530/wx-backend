from .base import db


class SearchKeyWord(db.Model):
    """
    搜索关键词
    """
    __tablename__ = 'search_key_word'
    id = db.Column(db.Integer(), primary_key=True)
    keyword = db.Column(db.String(100),doc='关键词')
    count = db.Column(db.Integer(), default=0,doc='搜索次数')
    is_hot = db.Column(db.Boolean, default=False,doc='是热点，默认值否')