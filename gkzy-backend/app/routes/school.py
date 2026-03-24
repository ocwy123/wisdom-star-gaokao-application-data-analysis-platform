from flask import Blueprint, request, jsonify
from app.extensions import cache
from app.services.school import SchoolService
from app.utils.response import success, error

school_bp = Blueprint('school', __name__, url_prefix='/api/school')


@school_bp.route('/list', methods=['GET'])
def get_school_list():
    """获取高校列表（支持分页和筛选）"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        province = request.args.get('province', None, type=str)
        city = request.args.get('city', None, type=str)
        school_type = request.args.get('type', None, type=str)
        is_985 = request.args.get('is_985', None, type=str)
        is_211 = request.args.get('is_211', None, type=str)
        is_double_first = request.args.get('is_double_first', None, type=str)
        keyword = request.args.get('keyword', None, type=str)
        
        # 转换布尔值参数
        def parse_bool(value):
            if value is None:
                return None
            if value.lower() in ['true', '1', 'yes']:
                return True
            elif value.lower() in ['false', '0', 'no']:
                return False
            return None
        
        # 生成缓存 key（包含所有参数）
        cache_key = f'school_list:{page}:{page_size}:{province or ""}:{city or ""}:{school_type or ""}:{is_985 or ""}:{is_211 or ""}:{is_double_first or ""}:{keyword or ""}'
        
        # 尝试从缓存获取
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        data = SchoolService.get_school_list(
            page=page,
            page_size=page_size,
            province=province,
            city=city,
            school_type=school_type,
            is_985=parse_bool(is_985),
            is_211=parse_bool(is_211),
            is_double_first=parse_bool(is_double_first),
            keyword=keyword
        )
        
        response = success(data=data)
        # 缓存 5 分钟
        cache.set(cache_key, response, timeout=300)
        
        return response
    except Exception as e:
        return error(message=str(e)), 500


@school_bp.route('/detail/<int:school_id>', methods=['GET'])
@cache.cached(timeout=300, key_prefix='school_detail')
def get_school_detail(school_id):
    """获取高校详情"""
    try:
        data = SchoolService.get_school_detail(school_id)
        
        if not data:
            return error(message='学校不存在'), 404
        
        return success(data=data)
    except Exception as e:
        return error(message=str(e)), 500


@school_bp.route('/provinces', methods=['GET'])
@cache.cached(timeout=3600, key_prefix='school_provinces')
def get_provinces():
    """获取所有省份列表"""
    try:
        data = SchoolService.get_provinces()
        return success(data=data)
    except Exception as e:
        return error(message=str(e)), 500


@school_bp.route('/cities', methods=['GET'])
def get_cities():
    """获取所有城市列表"""
    try:
        province = request.args.get('province', None, type=str)
        
        # 生成缓存 key（包含省份参数）
        cache_key = f'school_cities:{province or "all"}'
        
        # 尝试从缓存获取
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        data = SchoolService.get_cities(province=province)
        response = success(data=data)
        # 缓存 1 小时
        cache.set(cache_key, response, timeout=3600)
        
        return response
    except Exception as e:
        return error(message=str(e)), 500


@school_bp.route('/types', methods=['GET'])
@cache.cached(timeout=3600, key_prefix='school_types')
def get_types():
    """获取所有学校类型列表"""
    try:
        data = SchoolService.get_types()
        return success(data=data)
    except Exception as e:
        return error(message=str(e)), 500
