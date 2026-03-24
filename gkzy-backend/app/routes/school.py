from flask import Blueprint, request, jsonify
from app.models.school import School
from app.extensions import db
from app.utils.response import success, error

# 创建蓝图
school_bp = Blueprint('school', __name__, url_prefix='/api/school')

@school_bp.route('/list', methods=['GET'])
def get_school_list():
    """获取学校列表"""
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        
        paginated = School.query.paginate(page=page, per_page=size, error_out=False)
        items = [s.to_dict() for s in paginated.items]
        
        return success(data={
            'list': items,
            'total': paginated.total,
            'page': page,
            'size': size
        })
    except Exception as e:
        print(f"Error in get_school_list: {str(e)}")
        return error(message=f"数据库查询失败: {str(e)}"), 500

@school_bp.route('/<int:school_id>', methods=['GET'])
@school_bp.route('/detail/<int:school_id>', methods=['GET'])
def get_school_detail(school_id):
    """获取学校详情"""
    try:
        school = School.query.get(school_id)
        if not school:
            return error('学校不存在', code=404)
        
        return success(data=school.to_dict())
    except Exception as e:
        print(f"Error in get_school_detail: {str(e)}")
        return error(message=f"查询失败: {str(e)}"), 500