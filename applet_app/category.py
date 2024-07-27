from flask import Blueprint, request, current_app, jsonify
from models import BookBigCategory, BookCategory, Book

"""
分类表
"""

category_bp = Blueprint('category', __name__, url_prefix='/categories')


@category_bp.route('/')
def category_list():
    """
    获取分类列表
    :return:
    """
    # 1.用户参数，获取性别参数，查询字符串
    gender = request.args.get('gender', 1, int)
    # 2.根据性别，查询大分类数据
    bk_big_category = BookBigCategory.query.filter(BookBigCategory.channel == gender).all()
    data = []

    # 3.遍历大分类列表数据，进行保存 channel = 1
    for book_category in bk_big_category:
        big_item = {
            'id': book_category.cate_id,
            'title': book_category.cate_name,
            'imgUrl': f"http://{current_app.config['QINIU_SETTINGS']['host']}/{book_category.icon}",
            'subCategory': []
        }
        for category in book_category.second_cates:
            temp = {
                'id': category.cate_id,
                'title': category.cate_name
            }
            big_item['subCategory'].append(temp)
        data.append(big_item)
    return jsonify(data)


"""
分类书籍列表 对书籍筛选
东方玄幻 == 东方玄幻 != 都市生活
根据字数筛选 == 50w === 50w != 100w

"""


@category_bp.route('/filters')
def category_book_list():
    # 1.获取参数:?cate_id=&words=5000000&oder =1&page&pagesize=&page_count
    page = request.args.get('page', 1, int)
    pagesize = request.args.get('pagesize', 10, int)
    category_id = request.args.get('category_id', 0, int)
    words = request.args.get('words', -1, int)
    order = request.args.get('order', 1, int)

    # 对参数进行校验
    if not category_id:
        return jsonify(msg="缺少分类id"), 400

    # 2.根据分类提交category_id,查询数据，查询书籍大分类数据
    categories = BookBigCategory.query.get(category_id)

    # 判断查询结果, 根据大分类数据，使用关系引用，获取二级分类数据
    seconds_id = set([i.cate_id for i in categories.second_cates])

    # 根据分类数据，查询书籍表，获取分类范围内的书籍的数据
    # -- 过滤查询，保存的是查询结果对象，因为，需要数据进行再次查询的操作
    query = Book.query.filter(Book.cate_id.in_(seconds_id))
    categories = BookCategory.query.filter_by(cate_id=Book.cate_id).all()
    # category_names = [i.cate_name for i in categories] 获取分类名称和列表

    # 根据字数条件words查询书籍数据
    if words == 1:
        query = query.filter(Book.word_count < 500000)

    elif words == 2:
        query = query.filter(Book.word_count.between(500000, 1000000))

    elif words == 3:
        query = query.filter(Book.word_count > 1000000)

    # 根据排序条件order, 按照最热、收藏数量来进行排序
    # 1 表示热度，2 表示收藏
    if order == 1:
        query = query.order_by(Book.heat.desc())

    elif order == 2:
        query = query.order_by(Book.collect_count.desc())

    else:
        return jsonify(msg="错误的排序选项"), 400

    paginate = query.paginate(page=page, per_page=pagesize, error_out=False)
    # 分类名称迭代

    books_list = paginate.items

    items = []

    # 遍历分页数据，获取每页数据、总页数
    for item in books_list:
        # category_name = next((category.cate_name for category in categories if category.cate_id == item.cate_id), None)

        items.append({
            'id': item.book_id,
            'title': item.book_name,
            'introduction': item.intro,
            'author': item.author_name,
            'state': item.status,
            'category_id': item.cate_id,
            'category_name': item.cate_name,
            'imgUrl': f"http://{current_app.config['QINIU_SETTINGS']['host']}/{item.cover}",
        })

    data = {
        'items': items,
        'pagesize': 10,
        'pages': paginate.pages,
        'page': paginate.page
    }
    return jsonify(data)
