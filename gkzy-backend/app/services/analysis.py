from flask import Blueprint, request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_, or_, desc, asc
from datetime import datetime
from functools import wraps
from app.extensions import db
import json
from app.services.admin_auth import (
    EduSchool, EduMajor, EduSchoolMajor, EduAdmRecord,
    AnaSchoolHeat, AnaMajorEmployment, AnaScoreSegment
)
import json
from datetime import datetime
analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

# ==================== 深度信息检索接口 ====================

@analysis_bp.route('/search', methods=['POST'])
def deep_search():
    """
    深度信息检索
    请求体: {
        "keyword": "搜索关键词",
        "types": ["school", "major", "employment"],  # 检索类型
        "filters": {  # 筛选条件
            "province": "北京市",
            "type": "理工类",
            "score_range": [500, 700],
            "year": 2024
        },
        "page": 1,
        "page_size": 20,
        "sort_by": "heat_score",
        "sort_order": "desc"
    }
    """
    try:
        data = request.get_json()
        keyword = data.get('keyword', '')
        search_types = data.get('types', ['school', 'major', 'employment'])
        filters = data.get('filters', {})
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)
        sort_by = data.get('sort_by', 'relevance')
        sort_order = data.get('sort_order', 'desc')
        
        results = []
        
        # 1. 学校检索
        if 'school' in search_types:
            schools = search_schools(keyword, filters)
            results.extend(schools)
        
        # 2. 专业检索
        if 'major' in search_types:
            majors = search_majors(keyword, filters)
            results.extend(majors)
        
        # 3. 就业数据检索
        if 'employment' in search_types:
            employment = search_employment(keyword, filters)
            results.extend(employment)
        
        # 4. 招生记录检索
        if 'admission' in search_types:
            admissions = search_admissions(keyword, filters)
            results.extend(admissions)
        
        # 5. 热度数据检索
        if 'heat' in search_types:
            heat_data = search_heat_data(keyword, filters)
            results.extend(heat_data)
        
        # 排序
        results = sort_results(results, sort_by, sort_order)
        
        # 分页
        total = len(results)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_results = results[start:end]
        
        return jsonify({
            'success': True,
            'data': {
                'items': paginated_results,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        })
        
    except Exception as e:
        print(f"搜索错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

def search_schools(keyword, filters):
    """搜索学校"""
    from app.services.admin_auth import EduSchool
    
    query = EduSchool.query
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                EduSchool.name.contains(keyword),
                EduSchool.code.contains(keyword),
                EduSchool.city.contains(keyword)
            )
        )
    
    # 筛选条件
    if filters.get('province'):
        query = query.filter(EduSchool.province == filters['province'])
    
    if filters.get('city'):
        query = query.filter(EduSchool.city.contains(filters['city']))
    
    if filters.get('school_type'):
        query = query.filter(EduSchool.type == filters['school_type'])
    
    if 'is_985' in filters:
        query = query.filter(EduSchool.is_985 == filters['is_985'])
    
    if 'is_211' in filters:
        query = query.filter(EduSchool.is_211 == filters['is_211'])
    
    schools = query.limit(50).all()
    
    results = []
    for school in schools:
        # 获取学校热度
        heat = get_school_heat(school.id)
        
        results.append({
            'id': school.id,
            'type': 'school',
            'name': school.name,
            'school_name': school.name,
            'code': school.code,
            'province': school.province,
            'city': school.city,
            'type_name': school.type,
            'is_985': school.is_985,
            'is_211': school.is_211,
            'is_double_first': school.is_double_first,
            'description': school.description,
            'heat_score': heat.get('heat_score', 0),
            'search_count': heat.get('search_count', 0),
            'favorite_count': heat.get('favorite_count', 0),
            'relevance': calculate_relevance(keyword, school.name)
        })
    
    return results

def search_majors(keyword, filters):
    """搜索专业"""
    from app.services.admin_auth import EduMajor
    
    query = EduMajor.query
    
    if keyword:
        query = query.filter(
            or_(
                EduMajor.name.contains(keyword),
                EduMajor.code.contains(keyword),
                EduMajor.degree.contains(keyword)
            )
        )
    
    majors = query.limit(50).all()
    
    results = []
    for major in majors:
        # 获取专业就业数据
        employment = get_major_employment(major.id)
        
        results.append({
            'id': major.id,
            'type': 'major',
            'name': major.name,
            'major_name': major.name,
            'code': major.code,
            'duration': major.duration,
            'degree': major.degree,
            'subjects': major.subjects,
            'description': major.description,
            'avg_salary': employment.get('avg_salary', 0),
            'employment_rate': employment.get('employment_rate', 0),
            'relevance': calculate_relevance(keyword, major.name)
        })
    
    return results

def search_employment(keyword, filters):
    """搜索就业数据"""
    from app.services.admin_auth import AnaMajorEmployment, EduMajor
    
    query = AnaMajorEmployment.query.join(
        EduMajor, AnaMajorEmployment.major_id == EduMajor.id
    )
    
    if keyword:
        query = query.filter(EduMajor.name.contains(keyword))
    
    if filters.get('year'):
        query = query.filter(AnaMajorEmployment.year == filters['year'])
    
    if filters.get('min_salary'):
        query = query.filter(AnaMajorEmployment.avg_salary >= filters['min_salary'])
    
    employment_data = query.limit(50).all()
    
    results = []
    for emp in employment_data:
        major = EduMajor.query.get(emp.major_id)
        
        results.append({
            'id': emp.id,
            'type': 'employment',
            'major_id': emp.major_id,
            'major_name': major.name if major else '未知',
            'year': emp.year,
            'avg_salary': emp.avg_salary,
            'industry_distribution': json.loads(emp.industry_distribution) if emp.industry_distribution else {},
            'post_distribution': json.loads(emp.post_distribution) if emp.post_distribution else {},
            'region_distribution': json.loads(emp.region_distribution) if emp.region_distribution else {},
            'prospect': emp.prospect
        })
    
    return results

def search_admissions(keyword, filters):
    """搜索招生记录"""
    from app.services.admin_auth import EduAdmRecord, EduSchool, EduMajor
    
    query = EduAdmRecord.query.join(
        EduSchool, EduAdmRecord.school_id == EduSchool.id
    ).join(
        EduMajor, EduAdmRecord.major_id == EduMajor.id
    )
    
    if keyword:
        query = query.filter(
            or_(
                EduSchool.name.contains(keyword),
                EduMajor.name.contains(keyword)
            )
        )
    
    if filters.get('province'):
        query = query.filter(EduAdmRecord.province == filters['province'])
    
    if filters.get('year'):
        query = query.filter(EduAdmRecord.year == filters['year'])
    
    if filters.get('batch'):
        query = query.filter(EduAdmRecord.batch == filters['batch'])
    
    if filters.get('subject'):
        query = query.filter(EduAdmRecord.subject == filters['subject'])
    
    if filters.get('score_range'):
        min_score, max_score = filters['score_range']
        query = query.filter(
            EduAdmRecord.min_score.between(min_score, max_score)
        )
    
    admissions = query.limit(50).all()
    
    results = []
    for adm in admissions:
        school = EduSchool.query.get(adm.school_id)
        major = EduMajor.query.get(adm.major_id)
        
        results.append({
            'id': adm.id,
            'type': 'admission',
            'school_id': adm.school_id,
            'school_name': school.name if school else '未知',
            'major_id': adm.major_id,
            'major_name': major.name if major else '未知',
            'province': adm.province,
            'year': adm.year,
            'plan_count': adm.plan_count,
            'subject': adm.subject,
            'batch': adm.batch,
            'major_group': adm.major_group,
            'min_score': adm.min_score,
            'min_rank': adm.min_rank
        })
    
    return results

def search_heat_data(keyword, filters):
    """搜索热度数据"""
    from app.services.admin_auth import AnaSchoolHeat, EduSchool
    
    query = AnaSchoolHeat.query.join(
        EduSchool, AnaSchoolHeat.school_id == EduSchool.id
    )
    
    if keyword:
        query = query.filter(EduSchool.name.contains(keyword))
    
    heat_data = query.limit(50).all()
    
    results = []
    for heat in heat_data:
        school = EduSchool.query.get(heat.school_id)
        
        results.append({
            'id': heat.id,
            'type': 'heat',
            'school_id': heat.school_id,
            'school_name': school.name if school else '未知',
            'search_count': heat.search_count,
            'favorite_count': heat.favorite_count,
            'view_count': heat.view_count,
            'heat_score': float(heat.heat_score) if heat.heat_score else 0
        })
    
    return results

def get_school_heat(school_id):
    """获取学校热度"""
    from app.services.admin_auth import AnaSchoolHeat
    
    heat = AnaSchoolHeat.query.filter_by(school_id=school_id).first()
    if heat:
        return {
            'heat_score': float(heat.heat_score) if heat.heat_score else 0,
            'search_count': heat.search_count,
            'favorite_count': heat.favorite_count,
            'view_count': heat.view_count
        }
    return {}

def get_major_employment(major_id):
    """获取专业就业数据"""
    from app.services.admin_auth import AnaMajorEmployment
    
    emp = AnaMajorEmployment.query.filter_by(major_id=major_id).first()
    if emp:
        return {
            'avg_salary': emp.avg_salary,
            'employment_rate': 0  # 需要根据实际数据计算
        }
    return {}

def calculate_relevance(keyword, text):
    """计算相关性得分"""
    if not keyword or not text:
        return 0
    keyword = keyword.lower()
    text = text.lower()
    if keyword in text:
        return 1.0 - (text.index(keyword) / len(text))
    return 0

def sort_results(results, sort_by, sort_order):
    """排序结果"""
    reverse = (sort_order == 'desc')
    
    if sort_by == 'relevance':
        return sorted(results, key=lambda x: x.get('relevance', 0), reverse=reverse)
    elif sort_by == 'heat_score':
        return sorted(results, key=lambda x: x.get('heat_score', 0), reverse=reverse)
    elif sort_by == 'avg_salary':
        return sorted(results, key=lambda x: x.get('avg_salary', 0), reverse=reverse)
    elif sort_by == 'min_score':
        return sorted(results, key=lambda x: x.get('min_score', 0), reverse=reverse)
    elif sort_by == 'name':
        return sorted(results, key=lambda x: x.get('name', ''), reverse=reverse)
    
    return results

# ==================== 多维对比分析接口 ====================

@analysis_bp.route('/compare', methods=['POST'])
def multi_dimension_compare():
    """
    多维对比分析
    请求体: {
        "dimension": "school",  # 对比维度（单选）
        "metrics": ["avg_score", "heat_score", "admission_rate"],  # 指标列表
        "filters": {  # 筛选条件
            "school_ids": [1, 2, 3],
            "major_ids": [1, 2],
            "provinces": ["北京市", "上海市"]
        },
        "time_range": [2020, 2024]
    }
    """
    try:
        data = request.get_json()
        dimension = data.get('dimension', 'school')
        metrics = data.get('metrics', ['avg_score', 'heat_score'])
        filters = data.get('filters', {})
        time_range = data.get('time_range', [2020, 2024])
        
        result = {
            'dimension': dimension,
            'metrics': metrics,
            'data': []
        }
        
        # 根据维度调用不同的分析函数
        if dimension == 'school':
            result['data'] = compare_schools(filters, metrics, time_range)
        elif dimension == 'major':
            result['data'] = compare_majors(filters, metrics, time_range)
        elif dimension == 'province':
            result['data'] = compare_by_province(filters, metrics, time_range)
        elif dimension == 'year':
            result['data'] = analyze_year_trend(filters, metrics, time_range)
        elif dimension == 'score':
            result['data'] = analyze_by_score_segment(filters, metrics, time_range)
        elif dimension == 'heat':
            result['data'] = analyze_heat_trend(filters, metrics, time_range)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print(f"对比分析错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
def compare_schools(filters, metrics, time_range):
    """学校对比分析"""
    from app.services.admin_auth import EduSchool, EduAdmRecord, AnaSchoolHeat
    
    school_ids = filters.get('school_ids', [])
    if not school_ids:
        return []
    
    result = []
    for school_id in school_ids:
        school = EduSchool.query.get(school_id)
        if not school:
            continue
        
        item = {
            'dimension': 'school',
            'dimension_value': school.name,
            'school_id': school_id,
            'data': {}
        }
        
        # 获取招生数据
        admissions = EduAdmRecord.query.filter(
            EduAdmRecord.school_id == school_id,
            EduAdmRecord.year.between(time_range[0], time_range[1])
        ).all()
        
        if 'avg_score' in metrics:
            scores = [a.min_score for a in admissions if a.min_score]
            item['data']['avg_score'] = sum(scores) / len(scores) if scores else 0
        
        if 'admission_rate' in metrics:
            # 计算录取率（需要实际数据）
            item['data']['admission_rate'] = 0.75  # 示例值
        
        if 'min_score' in metrics:
            item['data']['min_score'] = min([a.min_score for a in admissions if a.min_score]) if admissions else 0
        
        if 'max_score' in metrics:
            item['data']['max_score'] = max([a.min_score for a in admissions if a.min_score]) if admissions else 0
        
        # 获取热度数据
        heat = AnaSchoolHeat.query.filter_by(school_id=school_id).first()
        if heat and 'heat_score' in metrics:
            item['data']['heat_score'] = float(heat.heat_score) if heat.heat_score else 0
        
        result.append(item)
    
    return result

def compare_majors(filters, metrics, time_range):
    """专业对比分析"""
    from app.services.admin_auth import EduMajor, AnaMajorEmployment, EduAdmRecord
    
    major_ids = filters.get('major_ids', [])
    if not major_ids:
        return []
    
    result = []
    for major_id in major_ids:
        major = EduMajor.query.get(major_id)
        if not major:
            continue
        
        item = {
            'dimension': 'major',
            'dimension_value': major.name,
            'major_id': major_id,
            'data': {}
        }
        
        # 获取就业数据
        employment = AnaMajorEmployment.query.filter_by(major_id=major_id).first()
        if employment:
            if 'avg_salary' in metrics:
                item['data']['avg_salary'] = employment.avg_salary
            if 'employment_rate' in metrics:
                item['data']['employment_rate'] = 0  # 需要实际数据
        
        # 获取招生数据
        admissions = EduAdmRecord.query.filter(
            EduAdmRecord.major_id == major_id,
            EduAdmRecord.year.between(time_range[0], time_range[1])
        ).all()
        
        if 'avg_score' in metrics:
            scores = [a.min_score for a in admissions if a.min_score]
            item['data']['avg_score'] = sum(scores) / len(scores) if scores else 0
        
        result.append(item)
    
    return result

def compare_by_province(filters, metrics, time_range):
    """按省份对比分析"""
    from app.services.admin_auth import EduSchool, EduAdmRecord
    
    provinces = filters.get('provinces', [])
    if not provinces:
        # 获取所有省份
        provinces = db.session.query(EduSchool.province).distinct().all()
        provinces = [p[0] for p in provinces if p[0]]
    
    result = []
    for province in provinces[:10]:  # 限制数量
        schools = EduSchool.query.filter_by(province=province).all()
        school_ids = [s.id for s in schools]
        
        if not school_ids:
            continue
        
        admissions = EduAdmRecord.query.filter(
            EduAdmRecord.school_id.in_(school_ids),
            EduAdmRecord.year.between(time_range[0], time_range[1])
        ).all()
        
        item = {
            'dimension': 'province',
            'dimension_value': province,
            'data': {}
        }
        
        if 'avg_score' in metrics:
            scores = [a.min_score for a in admissions if a.min_score]
            item['data']['avg_score'] = sum(scores) / len(scores) if scores else 0
        
        if 'school_count' in metrics:
            item['data']['school_count'] = len(schools)
        
        if 'admission_count' in metrics:
            item['data']['admission_count'] = len(admissions)
        
        result.append(item)
    
    return result

def analyze_year_trend(filters, metrics, time_range):
    """年份趋势分析"""
    from app.services.admin_auth import EduAdmRecord
    
    result = []
    for year in range(time_range[0], time_range[1] + 1):
        query = EduAdmRecord.query.filter_by(year=year)
        
        if filters.get('school_ids'):
            query = query.filter(EduAdmRecord.school_id.in_(filters['school_ids']))
        
        if filters.get('major_ids'):
            query = query.filter(EduAdmRecord.major_id.in_(filters['major_ids']))
        
        admissions = query.all()
        
        item = {
            'dimension': 'year',
            'dimension_value': year,
            'data': {}
        }
        
        if 'avg_score' in metrics:
            scores = [a.min_score for a in admissions if a.min_score]
            item['data']['avg_score'] = sum(scores) / len(scores) if scores else 0
        
        if 'admission_count' in metrics:
            item['data']['admission_count'] = len(admissions)
        
        if 'plan_count' in metrics:
            item['data']['plan_count'] = sum([a.plan_count for a in admissions if a.plan_count])
        
        result.append(item)
    
    return result

def analyze_by_score_segment(filters, metrics, time_range):
    """分数段分析"""
    from app.services.admin_auth import EduAdmRecord
    
    segments = [
        {'name': '600分以上', 'min': 600, 'max': 750},
        {'name': '550-600分', 'min': 550, 'max': 600},
        {'name': '500-550分', 'min': 500, 'max': 550},
        {'name': '450-500分', 'min': 450, 'max': 500},
        {'name': '400-450分', 'min': 400, 'max': 450},
        {'name': '400分以下', 'min': 0, 'max': 400}
    ]
    
    result = []
    for segment in segments:
        query = EduAdmRecord.query.filter(
            EduAdmRecord.min_score.between(segment['min'], segment['max']),
            EduAdmRecord.year.between(time_range[0], time_range[1])
        )
        
        if filters.get('province'):
            query = query.filter(EduAdmRecord.province == filters['province'])
        
        admissions = query.all()
        
        item = {
            'dimension': 'score_segment',
            'dimension_value': segment['name'],
            'data': {
                'count': len(admissions)
            }
        }
        
        if 'school_count' in metrics:
            school_ids = set([a.school_id for a in admissions])
            item['data']['school_count'] = len(school_ids)
        
        if 'major_count' in metrics:
            major_ids = set([a.major_id for a in admissions])
            item['data']['major_count'] = len(major_ids)
        
        result.append(item)
    
    return result

def analyze_heat_trend(filters, metrics, time_range):
    """热度趋势分析"""
    from app.services.admin_auth import AnaSchoolHeat, EduSchool
    
    query = AnaSchoolHeat.query.join(
        EduSchool, AnaSchoolHeat.school_id == EduSchool.id
    )
    
    if filters.get('province'):
        query = query.filter(EduSchool.province == filters['province'])
    
    if filters.get('school_type'):
        query = query.filter(EduSchool.type == filters['school_type'])
    
    heat_data = query.all()
    
    # 按热度分数排序
    heat_data.sort(key=lambda x: x.heat_score or 0, reverse=True)
    
    result = []
    for heat in heat_data[:20]:  # 前20名
        school = EduSchool.query.get(heat.school_id)
        
        item = {
            'dimension': 'heat',
            'dimension_value': school.name if school else '未知',
            'data': {
                'heat_score': float(heat.heat_score) if heat.heat_score else 0,
                'search_count': heat.search_count,
                'favorite_count': heat.favorite_count,
                'view_count': heat.view_count
            }
        }
        
        result.append(item)
    
    return result

# ==================== 高级筛选接口 ====================

@analysis_bp.route('/filters', methods=['GET'])
def get_filter_options():
    """获取筛选选项"""
    try:
        from app.services.admin_auth import EduSchool, EduMajor
        
        # 获取省份列表
        provinces = db.session.query(EduSchool.province).distinct().all()
        provinces = [p[0] for p in provinces if p[0]]
        
        # 获取学校类型列表
        school_types = db.session.query(EduSchool.type).distinct().all()
        school_types = [t[0] for t in school_types if t[0]]
        
        # 获取专业列表
        majors = EduMajor.query.all()
        major_list = [{'id': m.id, 'name': m.name} for m in majors]
        # 获取学校列表
        schools = EduSchool.query.all()
        school_list = [{'id': s.id, 'name': s.name} for s in schools]
        # 获取年份范围
        from app.services.admin_auth import EduAdmRecord
        years = db.session.query(EduAdmRecord.year).distinct().order_by(EduAdmRecord.year).all()
        years = [y[0] for y in years if y[0]]
        
        return jsonify({
            'success': True,
            'data': {
                'provinces': provinces,
                'school_types': school_types,
                'majors': major_list,
                'schools': school_list,
                'years': years,
                'score_ranges': [
                    {'min': 0, 'max': 400, 'label': '400分以下'},
                    {'min': 400, 'max': 450, 'label': '400-450分'},
                    {'min': 450, 'max': 500, 'label': '450-500分'},
                    {'min': 500, 'max': 550, 'label': '500-550分'},
                    {'min': 550, 'max': 600, 'label': '550-600分'},
                    {'min': 600, 'max': 750, 'label': '600分以上'}
                ]
            }
        })
        
    except Exception as e:
        print(f"获取筛选选项错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== 导出分析结果 ====================

@analysis_bp.route('/export', methods=['POST'])
def export_analysis():
    """导出分析结果"""
    try:
        data = request.get_json()
        export_type = data.get('type', 'csv')  # csv, excel, json
        result_data = data.get('data', [])
        
        if export_type == 'json':
            return jsonify({
                'success': True,
                'data': result_data
            })
        
        elif export_type == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            if result_data:
                writer = csv.DictWriter(output, fieldnames=result_data[0].keys())
                writer.writeheader()
                writer.writerows(result_data)
            
            return jsonify({
                'success': True,
                'data': output.getvalue(),
                'format': 'csv'
            })
        
        return jsonify({'success': False, 'message': '不支持的导出格式'})
        
    except Exception as e:
        print(f"导出错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500