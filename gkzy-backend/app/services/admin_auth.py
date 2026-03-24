from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from functools import wraps
from app.extensions import db
import json
# 创建蓝图
admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/api/admin')

# ==================== 导入模型 ====================
from app.models.admin import Admin
from app.models.config_log import ConfigLog
from app.models.config import Config as SystemConfig
# ==================== 用户模型（从user.py导入）====================
from app.models.user import User

# ==================== 验证装饰器 ====================
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        try:
            secret_key = current_app.config.get('JWT_SECRET_KEY')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            current_admin = Admin.query.get(payload['admin_id'])
            
            if not current_admin:
                return jsonify({'success': False, 'message': '管理员不存在'}), 401
            
            if current_admin.status != 1:
                return jsonify({'success': False, 'message': '账号已被禁用'}), 401
            
            return f(current_admin, *args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': '登录已过期，请重新登录'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': '无效的令牌'}), 401
        except Exception as e:
            print(f"Token验证错误: {e}")
            return jsonify({'success': False, 'message': '认证失败'}), 401
            
    return decorated

# ==================== 管理员接口 ====================

@admin_auth_bp.route('/register', methods=['POST'])
def register():
    """管理员注册"""
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'请填写{field}'}), 400
    
    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少6位'}), 400
    
    if Admin.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    if Admin.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': '邮箱已被注册'}), 400
    
    role = 'super_admin' if Admin.query.count() == 0 else 'admin'
    
    admin = Admin(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        real_name=data.get('real_name', ''),
        role=role
    )
    
    try:
        db.session.add(admin)
        db.session.commit()
        
        secret_key = current_app.config.get('JWT_SECRET_KEY')
        token = jwt.encode({
            'admin_id': admin.id,
            'username': admin.username,
            'role': admin.role,
            'exp': datetime.utcnow() + timedelta(hours=2)
        }, secret_key)
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {
                'token': token,
                'admin': {
                    'id': admin.id,
                    'username': admin.username,
                    'email': admin.email,
                    'real_name': admin.real_name,
                    'role': admin.role,
                    'created_at': admin.created_at.strftime('%Y-%m-%d %H:%M:%S') if admin.created_at else None
                }
            }
        })
    except Exception as e:
        db.session.rollback()
        print(f"注册错误: {e}")
        return jsonify({'success': False, 'message': '注册失败，请稍后重试'}), 500

@admin_auth_bp.route('/login', methods=['POST'])
def login():
    """管理员登录"""
    data = request.get_json()
    
    account = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not account or not password:
        return jsonify({'success': False, 'message': '请填写用户名和密码'}), 400
    
    admin = Admin.query.filter(
        (Admin.username == account) | (Admin.email == account)
    ).first()
    
    if not admin or not check_password_hash(admin.password_hash, password):
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
    secret_key = current_app.config.get('JWT_SECRET_KEY')
    token = jwt.encode({
        'admin_id': admin.id,
        'username': admin.username,
        'role': admin.role,
        'exp': datetime.utcnow() + timedelta(hours=2)
    }, secret_key)
    
    return jsonify({
        'success': True,
        'message': '登录成功',
        'data': {
            'token': token,
            'admin': {
                'id': admin.id,
                'username': admin.username,
                'email': admin.email,
                'real_name': admin.real_name,
                'role': admin.role,
                'created_at': admin.created_at.strftime('%Y-%m-%d %H:%M:%S') if admin.created_at else None
            }
        }
    })

@admin_auth_bp.route('/logout', methods=['POST'])
@admin_required
def logout(current_admin):
    """管理员登出"""
    return jsonify({'success': True, 'message': '退出登录成功'})

@admin_auth_bp.route('/profile', methods=['GET'])
@admin_required
def get_profile(current_admin):
    """获取当前管理员信息"""
    return jsonify({
        'success': True,
        'data': {
            'id': current_admin.id,
            'username': current_admin.username,
            'email': current_admin.email,
            'real_name': current_admin.real_name,
            'role': current_admin.role,
            'created_at': current_admin.created_at.strftime('%Y-%m-%d %H:%M:%S') if current_admin.created_at else None
        }
    })

@admin_auth_bp.route('/profile', methods=['PUT'])
@admin_required
def update_profile(current_admin):
    """更新当前管理员信息"""
    data = request.get_json()
    
    if 'real_name' in data:
        current_admin.real_name = data['real_name']
    if 'email' in data and data['email'] != current_admin.email:
        if Admin.query.filter(Admin.email == data['email'], Admin.id != current_admin.id).first():
            return jsonify({'success': False, 'message': '邮箱已被其他管理员使用'}), 400
        current_admin.email = data['email']
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '个人信息更新成功'})
    except Exception as e:
        db.session.rollback()
        print(f"更新个人信息错误: {e}")
        return jsonify({'success': False, 'message': '更新失败'}), 500

@admin_auth_bp.route('/change-password', methods=['PUT'])
@admin_required
def change_password(current_admin):
    """修改密码"""
    data = request.get_json()
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'success': False, 'message': '请填写原密码和新密码'}), 400
    
    if not check_password_hash(current_admin.password_hash, old_password):
        return jsonify({'success': False, 'message': '原密码错误'}), 401
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码至少6位'}), 400
    
    current_admin.password_hash = generate_password_hash(new_password)
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '密码修改成功'})
    except Exception as e:
        db.session.rollback()
        print(f"修改密码错误: {e}")
        return jsonify({'success': False, 'message': '密码修改失败'}), 500

# ==================== 用户管理接口 ====================

@admin_auth_bp.route('/users', methods=['GET'])
@admin_required
def get_users(current_admin):
    """获取所有用户列表"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users]
        })
    except Exception as e:
        print(f"获取用户列表错误: {e}")
        return jsonify({'success': False, 'message': '获取用户列表失败'}), 500

@admin_auth_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(current_admin, user_id):
    """获取单个用户详情"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'success': True,
            'data': user.to_dict()
        })
    except Exception as e:
        print(f"获取用户详情错误: {e}")
        return jsonify({'success': False, 'message': '用户不存在'}), 404

@admin_auth_bp.route('/users', methods=['POST'])
@admin_required
def create_user(current_admin):
    """创建新用户"""
    data = request.get_json()
    
    required_fields = ['username', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'message': f'请填写{field}'}), 400
    
    username = data['username'].strip()
    password = data['password']
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少6位'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    email = data.get('email', '').strip().lower()
    if email and User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': '邮箱已被使用'}), 400
    
    # 使用实际的字段名
    user = User(
        username=username,
        password=generate_password_hash(password),
        nickname=data.get('nickname') or data.get('real_name', ''),
        phone=data.get('phone', ''),
        email=email,
        role=data.get('role', '普通用户'),
        status=data.get('status', 0)  # 根据您的表，默认是0
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '用户创建成功',
            'data': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        print(f"创建用户错误: {e}")
        return jsonify({'success': False, 'message': '创建失败'}), 500

@admin_auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(current_admin, user_id):
    """更新用户信息"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'nickname' in data:
        user.nickname = data['nickname']
    elif 'real_name' in data:
        user.nickname = data['real_name']
    
    if 'phone' in data:
        user.phone = data['phone']
    
    if 'email' in data and data['email'] != user.email:
        email = data['email'].strip().lower()
        if email and User.query.filter(User.email == email, User.id != user_id).first():
            return jsonify({'success': False, 'message': '邮箱已被其他用户使用'}), 400
        user.email = email
    
    if 'role' in data:
        user.role = data['role']
    
    if 'status' in data:
        user.status = data['status']
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '用户更新成功',
            'data': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        print(f"更新用户错误: {e}")
        return jsonify({'success': False, 'message': '更新失败'}), 500

@admin_auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(current_admin, user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': '用户删除成功'})
    except Exception as e:
        db.session.rollback()
        print(f"删除用户错误: {e}")
        return jsonify({'success': False, 'message': '删除失败'}), 500

@admin_auth_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(current_admin, user_id):
    """重置用户密码"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    new_password = data.get('new_password')
    if not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码至少6位'}), 400
    
    try:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'success': True, 'message': '密码重置成功'})
    except Exception as e:
        db.session.rollback()
        print(f"重置密码错误: {e}")
        return jsonify({'success': False, 'message': '重置失败'}), 500

@admin_auth_bp.route('/users/search', methods=['GET'])
@admin_required
def search_users(current_admin):
    """搜索用户"""
    keyword = request.args.get('keyword', '').strip()
    
    if not keyword:
        return jsonify({'success': False, 'message': '请输入搜索关键词'}), 400
    
    try:
        users = User.query.filter(
            (User.username.contains(keyword)) |
            (User.nickname.contains(keyword)) |
            (User.email.contains(keyword))
        ).all()
        
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users]
        })
    except Exception as e:
        print(f"搜索用户错误: {e}")
        return jsonify({'success': False, 'message': '搜索失败'}), 500

# ==================== 健康检查 ====================

@admin_auth_bp.route('/health', methods=['GET'])
def health():
    """健康检查接口"""
    try:
        db.session.execute('SELECT 1')
        return jsonify({
            'success': True,
            'message': '服务正常',
            'data': {
                'database': 'connected',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'数据库连接异常: {e}'
        }), 500

@admin_auth_bp.route('/check-database', methods=['GET'])
def check_database():
    """检查数据库中的所有表和用户表字段"""
    result = {
        'success': True,
        'database': 'gkzy_mysql',
        'tables': [],
        'admin_table_fields': [],
        'user_table_fields': [],
        'admin_table_exists': False,
        'user_table_exists': False
    }
    
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        tables = inspector.get_table_names()
        result['tables'] = tables
        
        result['admin_table_exists'] = 'admins' in tables
        result['user_table_exists'] = 'usr_user' in tables
        
        # 获取 admins 表字段
        if result['admin_table_exists']:
            columns = inspector.get_columns('admins')
            for col in columns:
                result['admin_table_fields'].append({
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col['nullable'],
                    'primary_key': col.get('primary_key', False)
                })
        
        # 获取 usr_user 表字段
        if result['user_table_exists']:
            columns = inspector.get_columns('usr_user')
            for col in columns:
                result['user_table_fields'].append({
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col['nullable'],
                    'primary_key': col.get('primary_key', False)
                })
        
        # 获取各表的记录数
        result['record_counts'] = {}
        for table in tables:
            try:
                count = db.session.execute(f'SELECT COUNT(*) FROM {table}').scalar()
                result['record_counts'][table] = count
            except:
                result['record_counts'][table] = '查询失败'
        
        # 获取示例数据
        if result['user_table_exists']:
            users = User.query.limit(5).all()
            result['sample_users'] = [user.to_dict() for user in users]
        
        if result['admin_table_exists']:
            admins = Admin.query.limit(5).all()
            result['sample_admins'] = [{
                'id': a.id,
                'username': a.username,
                'email': a.email,
                'real_name': a.real_name,
                'role': a.role,
                'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S') if a.created_at else None
            } for a in admins]
        
        return jsonify({
            'success': True,
            'message': '数据库检查完成',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'数据库检查失败: {str(e)}',
            'error': str(e)
        }), 500
# ==================== 系统配置接口 ====================

@admin_auth_bp.route('/system/config', methods=['GET'])
@admin_required
def get_system_config(current_admin):
    """获取所有系统配置"""
    try:
        configs = SystemConfig.query.all()
        result = {
            'datasource': {},
            'cache': {},
            'log': {},
            'system': {}
        }
        
        for config in configs:
            try:
                # 尝试解析JSON
                value = json.loads(config.config_value)
            except:
                value = config.config_value
            
            result[config.config_type][config.config_key] = value
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        print(f"获取配置错误: {e}")
        return jsonify({'success': False, 'message': '获取配置失败'}), 500

@admin_auth_bp.route('/system/config', methods=['POST'])
@admin_required
def save_system_config(current_admin):
    """保存系统配置"""
    data = request.get_json()
    
    try:
        # 获取客户端IP
        ip = request.remote_addr
        
        for config_type, configs in data.items():
            for key, value in configs.items():
                # 查找现有配置
                config = SystemConfig.query.filter_by(
                    config_type=config_type,
                    config_key=key
                ).first()
                
                old_value = None
                if config:
                    old_value = config.config_value
                    config.config_value = json.dumps(value, ensure_ascii=False)
                    config.updated_by = current_admin.id
                    config.updated_at = datetime.now()
                else:
                    # 创建新配置
                    config = SystemConfig(
                        config_key=key,
                        config_value=json.dumps(value, ensure_ascii=False),
                        config_type=config_type,
                        updated_by=current_admin.id
                    )
                    db.session.add(config)
                
                # 记录日志
                log = ConfigLog(
                    admin_id=current_admin.id,
                    action='UPDATE' if old_value else 'CREATE',
                    config_key=f"{config_type}.{key}",
                    old_value=old_value,
                    new_value=json.dumps(value, ensure_ascii=False),
                    ip_address=ip
                )
                db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '配置保存成功'
        })
    except Exception as e:
        db.session.rollback()
        print(f"保存配置错误: {e}")
        return jsonify({'success': False, 'message': '保存失败'}), 500

@admin_auth_bp.route('/system/config/logs', methods=['GET'])
@admin_required
def get_config_logs(current_admin):
    """获取配置变更日志"""
    try:
        logs = ConfigLog.query.order_by(ConfigLog.created_at.desc()).limit(50).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': log.id,
                'admin': log.admin.username if log.admin else '未知',
                'action': log.action,
                'config_key': log.config_key,
                'old_value': log.old_value,
                'new_value': log.new_value,
                'ip': log.ip_address,
                'time': log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else None
            } for log in logs]
        })
    except Exception as e:
        print(f"获取日志错误: {e}")
        return jsonify({'success': False, 'message': '获取日志失败'}), 500

@admin_auth_bp.route('/system/config/validate', methods=['POST'])
@admin_required
def validate_config(current_admin):
    """验证配置参数"""
    data = request.get_json()
    config_type = data.get('type')
    key = data.get('key')
    value = data.get('value')
    
    errors = []
    
    # 根据配置类型进行验证
    if config_type == 'datasource':
        if key == 'api_url':
            import re
            if not re.match(r'^https?://', value):
                errors.append('API地址必须以 http:// 或 https:// 开头')
        elif key == 'db_port':
            try:
                port = int(value)
                if port < 1 or port > 65535:
                    errors.append('端口必须在1-65535之间')
            except:
                errors.append('端口必须是数字')
    
    elif config_type == 'cache':
        if key == 'expire_time':
            try:
                time = int(value)
                if time < 1 or time > 86400:
                    errors.append('过期时间必须在1-86400秒之间')
            except:
                errors.append('过期时间必须是数字')
        elif key == 'capacity':
            try:
                cap = int(value)
                if cap < 1 or cap > 10000:
                    errors.append('容量必须在1-10000MB之间')
            except:
                errors.append('容量必须是数字')
    
    elif config_type == 'system':
        if key == 'timeout':
            try:
                timeout = int(value)
                if timeout < 1 or timeout > 300:
                    errors.append('超时时间必须在1-300秒之间')
            except:
                errors.append('超时时间必须是数字')
        elif key == 'max_concurrent':
            try:
                maxc = int(value)
                if maxc < 1 or maxc > 10000:
                    errors.append('最大并发用户数必须在1-10000之间')
            except:
                errors.append('最大并发用户数必须是数字')
        elif key == 'max_file_size':
            try:
                size = int(value)
                if size < 1 or size > 1024:
                    errors.append('文件大小限制必须在1-1024MB之间')
            except:
                errors.append('文件大小限制必须是数字')
    
    return jsonify({
        'success': len(errors) == 0,
        'errors': errors
    })
# ==================== 教育相关模型 ====================

class EduSchool(db.Model):
    """学校信息表"""
    __tablename__ = 'edu_school'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    is_985 = db.Column(db.Boolean, nullable=False)
    is_211 = db.Column(db.Boolean, nullable=False)
    is_double_first = db.Column(db.Boolean, nullable=False)
    founded_year = db.Column(db.Integer)
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    logo = db.Column(db.String(255))
    phd_count = db.Column(db.Integer)
    master_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class EduMajor(db.Model):
    """专业信息表"""
    __tablename__ = 'edu_major'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    degree = db.Column(db.String(50))
    subjects = db.Column(db.Text)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class EduSchoolMajor(db.Model):
    """学校专业关联表"""
    __tablename__ = 'edu_school_major'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    school_id = db.Column(db.BigInteger, db.ForeignKey('edu_school.id'), nullable=False)
    major_id = db.Column(db.BigInteger, db.ForeignKey('edu_major.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class EduAdmRecord(db.Model):
    """招生记录表"""
    __tablename__ = 'edu_adm_record'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    school_id = db.Column(db.BigInteger, db.ForeignKey('edu_school.id'), nullable=False)
    major_id = db.Column(db.BigInteger, db.ForeignKey('edu_major.id'), nullable=False)
    province = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    plan_count = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    batch = db.Column(db.String(50), nullable=False)
    major_group = db.Column(db.String(20), nullable=False)
    min_score = db.Column(db.Integer, nullable=False)
    min_rank = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class AnaSchoolHeat(db.Model):
    """学校热度表"""
    __tablename__ = 'ana_school_heat'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    school_id = db.Column(db.BigInteger, db.ForeignKey('edu_school.id'), nullable=False)
    search_count = db.Column(db.Integer, nullable=False)
    favorite_count = db.Column(db.Integer, nullable=False)
    view_count = db.Column(db.Integer, nullable=False)
    heat_score = db.Column(db.Numeric(10,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class AnaMajorEmployment(db.Model):
    """专业就业表"""
    __tablename__ = 'ana_major_employment'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    major_id = db.Column(db.BigInteger, db.ForeignKey('edu_major.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    avg_salary = db.Column(db.Integer)
    industry_distribution = db.Column(db.Text)
    post_distribution = db.Column(db.Text)
    region_distribution = db.Column(db.Text)
    prospect = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class AnaScoreSegment(db.Model):
    """分数段表"""
    __tablename__ = 'ana_score_segment'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    province = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(20), nullable=False)
    batch = db.Column(db.String(50))
    score = db.Column(db.Integer, nullable=False)
    rank = db.Column(db.Integer, nullable=False)
    same_score_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)