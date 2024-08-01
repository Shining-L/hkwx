from . import db
from sqlalchemy.sql import func


class BrowseHistory(db.Model):
    """
    浏览记录
    """
    __tablename__ = 'browse_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'))

    book = db.relationship('Book', uselist=False)
    # 第一次保存数据的时候实现一次
    created = db.Column(db.DateTime(), server_default=func.now())
    # fun.now()用于获取当前的日期和时间 更新每一次修改都要保存时间
    updated = db.Column(db.DateTime(), server_default=func.now())
