from flask import Blueprint, request, jsonify, current_app
from models import SearchKeyWord, Book, db
from sqlalchemy import not_

search_bp = Blueprint('search', __name__, url_prefix='/search')


@search_bp.route('/tags', methods=['GET'])
def tags_list():
    """
    1.获取参数，用户搜索的关键词keyword
    2.校验参数
    3.根据参数，查询数据，搜索关键词的表进行过滤查询,过滤关键词
    4. 热门的关键字，默认提供10条数据
    5.返回查询结果
    :return:
    """
    # 1.获取参数，用户搜索的关键词keyword
    key_word = request.args.get('keyword')

    # 2.校验参数
    if not key_word:
        return jsonify([])

    # 3.根据参数，查询数据，搜索关键词的表进行过滤查询,过滤关键词
    search_key = SearchKeyWord.query.filter(SearchKeyWord.keyword.contains(key_word)).limit(10)

    for index in search_key:
        # 4. 返回查询结果
        data = [{
            "title": index.keyword,
            "isHot": index.is_hot

        }]

        return jsonify(data)


@search_bp.route('/books')
def search_books():
    # 获取参数 ?key_word&page/pagesize
    key_word = request.args.get('key_word')
    page = request.args.get('page', 1, type=int)
    pagesize = request.args.get('pagesize', 10, type=int)

    # 2.判断关键字是否存在
    if not key_word:
        return jsonify(msg="参数错误")

    # 3.如果存在关键字，按照书籍名称进行包含关键字过滤查询
    query = Book.query.filter(Book.book_name.contains(key_word))

    # 4. 对查询结果进行分页处理
    # pagination对象 (保存了分页结果的信息，总页数，当前页码，每页数据)
    paginate = query.paginate(page=page, per_page=pagesize, error_out=False)
    # 获取分野之后的书本数据
    book_list = paginate.items
    items = []

    # 遍历分页结果， 保存数据到items
    for book in book_list:
        items.append({
            'id': book.book_id,
            'title': book.book_name,
            'intro': book.intro,
            'author': book.author_name,
            'state': book.status,
            'category_id': book.cate_id,
            'cate_name': book.cate_name,
            'imgUrl': f"http://{current_app.config['QINIU_SETTINGS']['host']}/{book.cover}"
        })
    data = {
        'counts': paginate.total,

        'pages': paginate.pages,
        'page': paginate.page,
        'items': items
    }

    return jsonify(data)


@search_bp.route('/recommends')
def recommends():
    """
    搜索推荐
      ○ 精准返回1条
      ○ 匹配返回2条
      ○ 推荐返回4条
    :return:
    """
    # 1.获取关键字
    keyword = request.args.get('key_word')
    # 2.根据关键词，查询关键词表
    skw = SearchKeyWord.query.filter(SearchKeyWord.keyword == keyword).first()

    # 3.判断查询结果，如果不存在，保存该关键词
    if skw is None:
        skw = SearchKeyWord(keyword=keyword, count=0)

    # 如果存在，让它的次数加1， 如果该关键词次数大于10，标记该该关键词为热门
    skw.count += 1
    if skw.count > 10:
        skw.is_hot = True
    db.session.add(skw)
    db.session.commit()

    # 推荐部分
    # ● 定义列表，用来存储书本的id，进行过滤查询的条件判断。
    # 书籍表里面，只有书名吗？ 书id
    book_list = []
    # 1条精确查询：根据关键词，查询书籍表，根据书籍名称匹配，保存数据
    accurate_data = Book.query.filter_by(book_name=keyword).first()

    accurate = {}

    if accurate_data:
        accurate = {
            'id': accurate_data.book_id,
            'title': accurate_data.book_name,
            'intro': accurate_data.intro,
            'state': accurate_data.status,
            'category_id': accurate_data.cate_id,
            'cate_name': accurate_data.cate_name,
            'imgUrl': f"http://{current_app.config['QINIU_SETTINGS']['host']}/{accurate_data.cover}"
        }

        book_list.append(accurate_data.book_id)
    #  kw = 大燕仙朝在都市 直接返回
    # 2条高匹配：查询书名包含关键词，并且该书不是1条精确查询的数据，提取2条，保存数据
    query = Book.query.filter(Book.book_name.contains(keyword), not_(Book.book_id.in_(book_list))).limit(2)
    match = []
    for book in query:
        match.append({
            'id': book.book_id,
            'title': book.book_name,
            'intro': book.intro,
            'state': book.status,
            'category_id': book.cate_id,
            'cate_name': book.cate_name,
            'imgUrl': f"http://{current_app.config['QINIU_SETTINGS']['host']}/{book.cover}"
        })
        book_list.append(book.book_id)
    # 4 条推荐：直接从书籍表过滤查询，不在列表范围内的书籍，取出4条作为推荐阅读。
    recommends_data = Book.query.filter(not_(Book.book_id.in_(book_list))).limit(4)
    recommends_list = []
    for book in recommends_data:
        recommends_list.append({
            'id': book.book_id,
            'title': book.book_name,
            'intro': book.intro,
            'state': book.status,
            'category_id': book.cate_id,
            'cate_name': book.cate_name,
            'imgUrl': f"http://{current_app.config['QINIU_SETTINGS']['host']}/{book.cover}"
        })

    data = {
        'accurate': accurate,
        'match': match,
        'recommends_list': recommends_list
    }

    return jsonify(data)