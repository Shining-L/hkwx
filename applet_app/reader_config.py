from flask import Blueprint, request, g, current_app, jsonify
from models import db, User
from utils.decoraters import login_required

config_bp = Blueprint('config', __name__, url_prefix="/config")


@config_bp.route('/preference', methods=["POST"])
@login_required
def preference():
    """
    1.获取性别参数
    2.查询数据库，获取用户信息

    :return:
    """
    gender = request.json.get("gender")
    gender = int(gender)

    if gender not in [0, 1]:
        return jsonify(msg="性别参数有误")

    user = User.query.filter_by(id=g.user_id).first()
    user.gender = gender

    db.session.add(user)
    db.session.commit()

    return jsonify(msg="设置成功")


# 配置信息
@config_bp.route('/read', methods=['POST'])
@login_required
def reader():
    brightness = request.json.get('brightness')
    font_size = request.json.get('font_size')
    background = request.json.get('background')
    turn = request.json.get('turn')

    # 查询数据 用户表， 根据用户id查询用户信息
    user = User.query.get(g.user_id)
    # 保存配置信息
    if brightness:
        user.brightness = brightness

    if font_size:
        user.fontSize = font_size

    if background:
        user.background = background

    if turn:
        user.turn = turn
    db.session.add(user)
    db.session.commit()

    return jsonify({'msg':"设置成功"})
