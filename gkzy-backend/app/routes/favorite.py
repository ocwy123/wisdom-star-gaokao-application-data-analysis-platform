from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.favorite import Favorite
from app.models.school import School
from app.models.major import Major
from app.routes.auth import token_required

# 创建收藏蓝图
favorite_bp = Blueprint('favorite', __name__, url_prefix='/api/favorite')

@favorite_bp.route('/add', methods=['POST'])
@token_required
def add_favorite(current_user):
    """添加收藏"""
    data = request.get_json()
    
    required_fields = ['favorite_type', 'target_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'缺少{field}参数'}), 400
    
    favorite_type = data['favorite_type']
    target_id = data['target_id']
    
    # 验证收藏类型
    if favorite_type not in ['school', 'major']:
        return jsonify({'success': False, 'message': '收藏类型错误'}), 400
    
    # 验证收藏对象是否存在
    if favorite_type == 'school':
        target = School.query.get(target_id)
    else:
        target = Major.query.get(target_id)
    
    if not target:
        return jsonify({'success': False, 'message': '收藏对象不存在'}), 404
    
    # 检查是否已经收藏
    existing_favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        favorite_type=favorite_type,
        target_id=target_id
    ).first()
    
    if existing_favorite:
        return jsonify({'success': False, 'message': '已经收藏过了'}), 400
    
    # 创建收藏记录
    favorite = Favorite(
        user_id=current_user.id,
        favorite_type=favorite_type,
        target_id=target_id
    )
    
    try:
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '收藏成功',
            'data': favorite.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '收藏失败'}), 500

@favorite_bp.route('/remove', methods=['POST'])
@token_required
def remove_favorite(current_user):
    """取消收藏"""
    data = request.get_json()
    
    required_fields = ['favorite_type', 'target_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'缺少{field}参数'}), 400
    
    favorite_type = data['favorite_type']
    target_id = data['target_id']
    
    # 查找收藏记录
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        favorite_type=favorite_type,
        target_id=target_id
    ).first()
    
    if not favorite:
        return jsonify({'success': False, 'message': '收藏记录不存在'}), 404
    
    try:
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '取消收藏成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '取消收藏失败'}), 500

@favorite_bp.route('/list', methods=['GET'])
@token_required
def get_favorites(current_user):
    """获取用户收藏列表"""
    favorite_type = request.args.get('type', 'all')  # all, school, major
    
    query = Favorite.query.filter_by(user_id=current_user.id)
    
    if favorite_type != 'all':
        query = query.filter_by(favorite_type=favorite_type)
    
    favorites = query.order_by(Favorite.created_at.desc()).all()
    
    # 获取收藏对象的详细信息
    result = []
    for favorite in favorites:
        favorite_data = favorite.to_dict()
        
        if favorite.favorite_type == 'school':
            school = School.query.get(favorite.target_id)
            if school:
                favorite_data['target_info'] = school.to_dict()
        else:
            major = Major.query.get(favorite.target_id)
            if major:
                favorite_data['target_info'] = major.to_dict()
        
        result.append(favorite_data)
    
    return jsonify({
        'success': True,
        'data': result
    })

@favorite_bp.route('/check', methods=['GET'])
@token_required
def check_favorite(current_user):
    """检查是否已收藏"""
    favorite_type = request.args.get('type')
    target_id = request.args.get('target_id')
    
    if not favorite_type or not target_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        favorite_type=favorite_type,
        target_id=target_id
    ).first()
    
    return jsonify({
        'success': True,
        'data': {
            'is_favorited': favorite is not None
        }
    })