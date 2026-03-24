from flask import Blueprint, request, jsonify
from app.models.major import Major
from app.models.major_employment import MajorEmployment
from app.models.school_major import SchoolMajor
from app.models.school import School
from app.extensions import db
from app.utils.response import success, error
from sqlalchemy import func, desc

major_bp = Blueprint('major', __name__, url_prefix='/api/major')


@major_bp.route('/list', methods=['GET'])
def get_major_list():
    """获取专业列表（支持分页和搜索）"""
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        keyword = request.args.get('keyword', '', type=str)

        query = Major.query
        if keyword:
            query = query.filter(Major.name.contains(keyword) | Major.code.contains(keyword))

        paginated = query.paginate(page=page, per_page=size, error_out=False)
        items = [m.to_dict() for m in paginated.items]

        return success(data={
            'list': items,
            'total': paginated.total,
            'page': page,
            'size': size
        })
    except Exception as e:
        print(f"Error in get_major_list: {str(e)}")  # 打印错误到控制台
        return error(message=f"数据库查询失败: {str(e)}"), 500


@major_bp.route('/<int:major_id>', methods=['GET'])
def get_major_detail(major_id):
    """获取专业详情"""
    major = Major.query.get(major_id)
    if not major:
        return error('专业不存在', code=404)

    return success(data=major.to_dict())


@major_bp.route('/<int:major_id>/employment', methods=['GET'])
def get_major_employment(major_id):
    """获取专业就业数据"""
    year = request.args.get('year', type=int)

    query = MajorEmployment.query.filter_by(major_id=major_id)
    if year:
        query = query.filter_by(year=year)

    # 默认获取最新年份数据
    employment = query.order_by(desc(MajorEmployment.year)).first()

    if not employment:
        return success(data={
            'major_id': major_id,
            'message': '暂无就业数据'
        })

    return success(data=employment.to_dict())


@major_bp.route('/<int:major_id>/schools', methods=['GET'])
def get_major_schools(major_id):
    """获取开设该专业的高校列表"""
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)

    # 查询开设该专业的高校
    query = db.session.query(
        SchoolMajor, School
    ).join(
        School, School.id == SchoolMajor.school_id
    ).filter(
        SchoolMajor.major_id == major_id
    )

    # 分页
    paginated = query.paginate(page=page, per_page=size, error_out=False)
    items = []
    for sm, school in paginated.items:
        items.append({
            'school_id': school.id,
            'school_name': school.name,
            'province': school.province,
            'city': school.city,
            'type': school.type,
            'is_985': school.is_985,
            'is_211': school.is_211,
            'is_double_first': school.is_double_first,
            'description': sm.description
        })

    return success(data={
        'list': items,
        'total': paginated.total,
        'page': page,
        'size': size
    })


@major_bp.route('/<int:major_id>/analysis', methods=['GET'])
def get_major_analysis(major_id):
    """获取专业深度分析数据（综合接口）"""
    # 1. 获取专业基本信息
    major = Major.query.get(major_id)
    if not major:
        return error('专业不存在', code=404)

    # 2. 获取最新就业数据
    employment = MajorEmployment.query.filter_by(major_id=major_id).order_by(desc(MajorEmployment.year)).first()

    # 3. 统计开设高校数量
    school_count = SchoolMajor.query.filter_by(major_id=major_id).count()

    # 4. 按省份统计开设高校分布
    province_distribution = db.session.query(
        School.province, func.count(School.id).label('count')
    ).join(
        SchoolMajor, School.id == SchoolMajor.school_id
    ).filter(
        SchoolMajor.major_id == major_id
    ).group_by(School.province).all()

    province_list = [{'province': p, 'count': c} for p, c in province_distribution]

    # 5. 获取往年就业趋势（近3年薪资）
    salary_trend = db.session.query(
        MajorEmployment.year, MajorEmployment.avg_salary
    ).filter(
        MajorEmployment.major_id == major_id
    ).order_by(MajorEmployment.year).limit(5).all()

    salary_data = [{'year': y, 'avg_salary': s} for y, s in salary_trend if s]

    # 6. 构建返回数据
    result = {
        'major_info': major.to_dict(),
        'school_count': school_count,
        'province_distribution': province_list,
        'salary_trend': salary_data,
        'employment': employment.to_dict() if employment else None
    }

    return success(data=result)

@major_bp.route('/test', methods=['GET'])
def test():
    return {"message": "major blueprint is working"}