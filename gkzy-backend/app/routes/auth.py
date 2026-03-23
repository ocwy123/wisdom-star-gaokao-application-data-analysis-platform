from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from functools import wraps
from app.extensions import db
from app.models.user import User

# 创建用户认证蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 验证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        try:
            secret_key = current_app.config.get('JWT_SECRET_KEY')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            current_user = User.query.get(payload['user_id'])
            
            if not current_user:
                return jsonify({'success': False, 'message': '用户不存在'}), 401
            
            if current_user.status != 0:
                return jsonify({'success': False, 'message': '账号已被禁用'}), 401
            
            return f(current_user, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': '登录已过期，请重新登录'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': '无效的令牌'}), 401
        except Exception as e:
            print(f"Token验证错误: {e}")
            return jsonify({'success': False, 'message': '认证失败'}), 401
            
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    required_fields = ['username', 'password', 'nickname']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'请填写{field}'}), 400
    
    username = data['username'].strip()
    password = data['password']
    nickname = data['nickname'].strip()
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少6位'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    # 检查邮箱是否重复
    email = data.get('email', '').strip().lower()
    if email and User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': '邮箱已被注册'}), 400
    
    # 检查手机号是否重复
    phone = data.get('phone', '').strip()
    if phone and User.query.filter_by(phone=phone).first():
        return jsonify({'success': False, 'message': '手机号已被注册'}), 400
    
    user = User(
        username=username,
        nickname=nickname,
        phone=phone,
        email=email,
        role='普通用户'
    )
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        
        secret_key = current_app.config.get('JWT_SECRET_KEY')
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, secret_key)
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {
                'token': token,
                'user': user.to_dict()
            }
        })
    except Exception as e:
        db.session.rollback()
        print(f"注册错误: {e}")
        return jsonify({'success': False, 'message': '注册失败，请稍后重试'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    account = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not account or not password:
        return jsonify({'success': False, 'message': '请填写用户名和密码'}), 400
    
    # 支持用户名、邮箱、手机号登录
    user = User.query.filter(
        (User.username == account) |
        (User.email == account) |
        (User.phone == account)
    ).first()
    
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    if user.status != 0:
        return jsonify({'success': False, 'message': '账号已被禁用'}), 401
    
    secret_key = current_app.config.get('JWT_SECRET_KEY')
    token = jwt.encode({
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, secret_key)
    
    return jsonify({
        'success': True,
        'message': '登录成功',
        'data': {
            'token': token,
            'user': user.to_dict()
        }
    })

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """用户登出"""
    return jsonify({'success': True, 'message': '退出登录成功'})

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """获取当前用户信息"""
    return jsonify({
        'success': True,
        'data': current_user.to_dict()
    })

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """更新当前用户信息"""
    data = request.get_json()
    
    if 'nickname' in data:
        current_user.nickname = data['nickname']
    
    if 'phone' in data and data['phone'] != current_user.phone:
        phone = data['phone'].strip()
        if phone and User.query.filter(User.phone == phone, User.id != current_user.id).first():
            return jsonify({'success': False, 'message': '手机号已被其他用户使用'}), 400
        current_user.phone = phone
    
    if 'email' in data and data['email'] != current_user.email:
        email = data['email'].strip().lower()
        if email and User.query.filter(User.email == email, User.id != current_user.id).first():
            return jsonify({'success': False, 'message': '邮箱已被其他用户使用'}), 400
        current_user.email = email
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '个人信息更新成功'})
    except Exception as e:
        db.session.rollback()
        print(f"更新个人信息错误: {e}")
        return jsonify({'success': False, 'message': '更新失败'}), 500

@auth_bp.route('/change-password', methods=['PUT'])
@token_required
def change_password(current_user):
    """修改密码"""
    data = request.get_json()
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'success': False, 'message': '请填写原密码和新密码'}), 400
    
    if not current_user.check_password(old_password):
        return jsonify({'success': False, 'message': '原密码错误'}), 401
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码至少6位'}), 400
    
    current_user.set_password(new_password)
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '密码修改成功'})
    except Exception as e:
        db.session.rollback()
        print(f"修改密码错误: {e}")
        return jsonify({'success': False, 'message': '密码修改失败'}), 500