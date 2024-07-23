"""
书架模块+
"""
from flask import Blueprint, g, current_app, jsonify
from utils.decoraters import login_required
# 书架表\书籍表\用户表
from models import BookShelf, db, Book, User
# 导入随机模块
import random

my_books_bp = Blueprint('mybook', __name__, url_prefix="/my_books")


# 定义路由，书架列表

@my_books_bp.route('/')
@login_required
def index():
    """
    1.书架必须是针对于某个用户看过的书籍返回.
    * 登陆状态(判断是哪个用户 user_id=1)
    * 查询用户的书籍表
    * 存在即返回
    * 不存在则默认返回5本书籍
    :return:
    """

    # 1.添加登陆验证装饰器
    user_id = g.user_id
    # 2.默认查询书架中的所有书籍数据，排序
    my_books = BookShelf.query.filter_by(user_id=user_id).order_by(BookShelf.created).all()
    # 创建空列表，存储书架书籍数据
    data = []
    # 3.判断查询结果,不存在
    if not my_books:
        # 如果书架里面没有书籍，从书籍表随机挑选5本书,存入书架中
        books = Book.query.all()  # 返回的Book对象的列表
        # population, 选择元素的序列或集合
        # k, 要选择的元素数量
        book_list = random.sample(books, 5)
        for bk in book_list:
            book_shelf = BookShelf(
                user_id=user_id,
                book_id=bk.book_id,
                book_name=bk.book_name,
                cover=bk.cover
            )

            # 提交数据
            db.session.add(book_shelf)
            data.append({"id": bk.book_id,
                         "title": bk.book_name,
                         "imgUrl": f"http://{current_app.config['QINIU_SETTINGS']['host']}/{bk.cover}"
                         })
        db.session.commit()
        return jsonify(data)
    else:
        # 4.存在则返回书籍数据
        for bk in my_books:
            data.append({"id": bk.book_id,
                         "title": bk.book_name,
                         "imgUrl": f"http://{current_app.config['QINIU_SETTINGS']['host']}/{bk.cover}"
                         })
        return jsonify(data)


# 定义路由，书籍管理--添加书籍
"""
1.添加登陆验证装饰器
2.接收参数，书籍id
3.根据书籍id,查询书籍表,确认数据的存在
4.查询书架表，确认该书在书架中是否存在
5.如果书架中不存在，则添加书籍
6.如果存在，返回
	{msg="书架中已存在当前书籍"}
	"""


@my_books_bp.route('/<book_id>', methods=['POST'])
@login_required
def add_book(book_id):
    """

    :param book_id: url固定参数，必须作为视图参数直接传入,flask中使用转换器进行处理，默认是字符串

    :return:
    """
    # 1.添加登陆验证装饰器
    user_id = g.user_id
    # 2.接收参数，书籍id

    # 3.根据书籍id, 查询书籍表, 确认数据的存在
    book = Book.query.filter(Book.book_id == book_id).first()
    if not book:
        return jsonify(msg="书籍不存在"), 404

    # 4.查询书架表，确认该书在书架中是否存在
    book_shelf = BookShelf.query.filter(BookShelf.user_id == user_id, BookShelf.book_id == book_id).first()
    if not book_shelf:
        # 5.如果书架中不存在，则添加书籍
        book_shelf = BookShelf(
            user_id=user_id,
            book_id=book.book_id,
            book_name=book.book_name,
            cover=book.cover
        )
        db.session.add(book_shelf)
        db.session.commit()
        # 返回添加成功的消息
        return jsonify(msg="添加成功")
    else:
        # 6.如果存在，则直接返回消息
        return jsonify(msg="书架中该书籍已存在")

# 定义路由，书籍管理--删除书籍
@my_books_bp.route('/<book_id>', methods=['DELETE'])
@login_required
def delete_book(book_id):
    # 1.添加登陆验证装饰器
    user_id = g.user_id
    # 2.查询书架表，确认该书在书架中是否存在
    book_shelf = BookShelf.query.filter(BookShelf.user_id == user_id, BookShelf.book_id == book_id).first()
    # 如果不存在，直接返回不存在的消息
    if not book_shelf:
        return jsonify(msg="该书籍在书架中不存在")

    db.session.delete(book_shelf)
    db.session.commit()
    return jsonify(msg="删除成功")