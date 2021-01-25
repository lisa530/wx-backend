from . import db
from sqlalchemy.sql import func


class BrowseHistory(db.Model):
    """
    浏览记录
    """
    __tablename__ = 'browse_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), doc='用户id外键')
    book_id = db.Column(db.Integer(), db.ForeignKey('book.book_id'), doc='书籍id外键')

    book = db.relationship('Book', uselist=False, doc='关系引用')
    created = db.Column(db.DateTime(), server_default=func.now(), doc='创建时间')
    updated = db.Column(db.DateTime(), server_default=func.now(), doc='修改时间')