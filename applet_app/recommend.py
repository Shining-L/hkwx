"""同类推荐"""
from flask import Blueprint, jsonify, current_app
from models import Book, BookBigCategory, db

re_bp = Blueprint('recommend', __name__, url_prefix='/re_end')


@re_bp.route('/hots/<int:cate_id>')
def hot_books(cate_id):
    """
    推荐 -- 同类热门推荐
    返回4条数据

    :param cate_id:
    :return:
    """
    # 根据参数分类id， 查询数据库,获取大分类数据
    big_cate = BookBigCategory.query.get(cate_id)
    books = []

    second_ids = [i.cate_id for i in big_cate.second_cates]

    # 根据分类，查询书籍表，获取对应分类的书籍数据，默认查询4条
    o_books = Book.query.filter(Book.cate_id.in_(second_ids)).limit(4).all()
    if not o_books:
        o_books = Book.query.limit(4).all()


    # 保存实际的基本信息
    for item in o_books:
        books.append({
            "author": item.author_name,
            "categoryID": item.cate_id,
            "categoryName": item.cate_name,
            "id": item.book_id,
            "imgURL": f"http://{current_app.config['QINIU_SETTINGS']['host']}/{item.cover}",
            "introduction": item.intro,
            "state": item.status,
            "title": item.book_name,
        })

    return jsonify(books)
