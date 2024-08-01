"""阅读"""
from flask import Blueprint, jsonify, g, current_app, request

from models import Book, BrowseHistory, db, BookChapters,BookChapterContent, ReadRate
from datetime import datetime

book_bp = Blueprint('book', __name__, url_prefix='/book')


# 目录
@book_bp.route('/chapters/<int:book_id>')
def chapter_list(book_id):
    page = request.args.get('page', 1, type=int)
    pagesize = request.args.get('pagesize', 10, type=int)
    order = request.args.get('order', 0, int)

    """
    1.根据书籍id查询id参数，查询书籍表
    2.查询书籍章节目录表，按照书籍id进行过滤查询
    3.根据order参数的排序条件
    4.对查询的结果进行分页处理
    5.遍历分页的数据，获取章节信息
    6.返回结果
    """
    book = Book.query.get(book_id)
    if not book:
        return jsonify(msg="书籍不存在"), 404

    # 2.查询书籍章节目录表，按照书籍id进行过滤查询
    query = BookChapters.query.filter(BookChapters.book_id == book_id)

    # 根据order参数的排序条件
    # 降序
    if order == 1:
        query = query.order_by(BookChapters.chapter_id.desc())
    else:
        query = query.order_by(BookChapters.chapter_id.asc())

    # 对查询的结果进行分页处理
    paginate = query.paginate(page=page, per_page=pagesize, error_out=False)
    data_list = paginate.items

    # 遍历分页的数据，获取章节信息
    items = []
    for data in data_list:
        items.append({
            'id': data.chapter_id,
            'title': data.chapter_name
        })

    # 构造响应信息
    chapter_data = {
        'counts': paginate.total,
        'page': paginate.page,
        'pages': paginate.pages,
        'item': items
    }
    return jsonify(chapter_data), 200

# 详情 根据书籍id进行查询
@book_bp.route('/<book_id>')
def book_detail(book_id):
    """
    1.根据书籍id进行查询数据库(书籍表)
    2.判断用户是否登陆
      1.如果用户登陆，查询数据库浏览记录、判断查询结果，保存浏览记录
      2.如果用户没有登陆，根据书籍id查询数据库书籍的章节表，默认按照倒序排序
    3.返回结果

    :param book_id:
    :return:
    """
    book = Book.query.get(book_id)
    if not book:
        return jsonify(msg="书籍不存在"), 404
    # 如果用户登陆，查询数据库浏览记录、判断查询结果，保存浏览记录
    if g.user_id:
        bs_data = BrowseHistory(user_id=g.user_id, book_id=book_id)
        # 判断查询结果
        if not bs_data:
            bs_data = BrowseHistory(user_id=g.user_id, book_id=book_id)
        bs_data.updated = datetime.now()

        db.session.add(bs_data)
        db.session.commit()

    # 如果用户没有登陆，根据书籍id查询数据库书籍的章节表，默认按照倒序排序 asc() 取最后一章 chapter_id
    chapter = BookChapters.query.filter_by(book_id=book_id).order_by(BookChapters.chapter_id.desc()).first()

    # 返回结果
    data = {
        "author": book.author_name,
        "categoryID": book.cate_id,
        "categoryName": book.cate_name,
        "id": book.book_id,
        "imgURL": f"http://{current_app.config['QINIU_SETTINGS']['host']}/{book.cover}",
        "introduction": book.intro,
        "lastChapter": chapter.chapter_name if chapter else None,
        "state": book.status,
        "title": book.book_name,
        "words": book.word_count
    }
    return jsonify(data), 200

# 阅读
@book_bp.route('/reader/<int:book_id>')
def reader_book(book_id):
    """
    1.根据书籍id，查询书籍表,确认书籍是否存在
    2.获取查询字符串中参数章节id,校验参数
    3.根据章节id,查询章节表
    4.判断查询结果

    :param book_id:
    :return:
    """
    # 根据书籍id，查询书籍表, 确认书籍是否存在
    book = Book.query.get(book_id)
    if not book:
        return jsonify(msg="书籍不存在"), 404

    # 获取查询字符串中参数章节id, 校验参数
    chapter_id = request.args.get("chapter_id", -1, type=int)
    if chapter_id < 1:
        return jsonify(msg="章节id不能小于1")

    # 根据章节id, 查询章节表
    chapter = BookChapters.query.filter_by(book_id=book_id, chapter_id=chapter_id).first()

    # 4.判段查询结果
    if not chapter:
        return jsonify(msg="章节不存在")

    # 5.如果数据存在，查询章节内容表
    content = BookChapterContent.query.filter_by(book_id=book_id, chapter_id=chapter_id).first()

    # 6.如果用户登陆，查询用户阅读进度表
    progress = None
    if g.user_id:
        progress = ReadRate.query.filter_by(book_id=book_id,chapter_id=chapter_id,user_id=g.user_id).first()


    data = {
        'id':book_id,
        'title': book.book_name,
        'chapter_id': chapter.chapter_id,
        'chapter_name': chapter.chapter_name,
        'progress': progress.rete if progress else 0,
        'article_content': content.content if content else ''
    }

    return jsonify(data)






