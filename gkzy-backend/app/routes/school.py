from flask import Blueprint, request, jsonify
from app.models.school import School
from app.extensions import db
from app.utils.response import success, error

school_bp = Blueprint('school', __name__, url_prefix='/api/school')

@school_bp.route('/list', methods=['GET'])
def get_school_list():
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    # 简单查询所有学校
    paginated = School.query.paginate(page=page, per_page=size, error_out=False)
    items = [s.to_dict() for s in paginated.items]
    return success(data={
        'list': items,
        'total': paginated.total,
        'page': page,
        'size': size
    })