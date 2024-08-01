"""浏览记录"""
from flask import Blueprint, jsonify, g, current_app, request

from models import BrowseHistory, db
from utils.decoraters import login_required

my_bp = Blueprint('history', __name__, url_prefix='/my')


# 路由
@my_bp.route('/histories')
def my_history():
    """
    1.查询数据库浏览记录，根据用户id查询
    2.获取到数据
    :return:
    """
    page = request.args.get("page", 1, int)
    size = request.args.get('pagesize', 10, int)

    paginate = BrowseHistory.query.filter_by(user_id=g.user_id).paginate(page=page, per_page=size, error_out=False)

    # 获取分页之后的数据
    history_data = paginate.items

    items = []

    for item in history_data:
        items.append({
            "id": item.book.book_id,
            "title": item.book.book_name,
            "author": item.book.author_name,
            "status": item.book.status,
            "imgURL": f"http://{current_app.config['QINIU_SETTINGS']['host']}/{item.book.cover}",
            "lastTime": item.updated.strftime('%Y-%m-%d %H:%M:%S')

        })
    data = {
        'counts': paginate.total,
        'size': size,
        'pages': paginate.pages,
        'page': paginate.page,
        'items': items
    }
    return jsonify(msg="success", data=data), 200


@my_bp.route('/histories', methods=["DELETE"])
@login_required
def delete_history():
    # 根据用户的id,查询浏览记录
    history_data = BrowseHistory.query.filter_by(user_id=g.user_id).all()
    # 遍历查询结果
    for data in history_data:
        db.session.delete(data)

    # 3.清除数据
    db.session.commit()

    return jsonify(msg='清除成功！')
