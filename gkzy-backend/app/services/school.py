from app.models.school import School
from app.models.adm_record import AdmRecord
from app import db
from sqlalchemy import func, distinct


class SchoolService:
    @staticmethod
    def get_school_list(page=1, page_size=20, province=None, city=None, school_type=None,
                        is_985=None, is_211=None, is_double_first=None, keyword=None):
        """获取高校列表（支持分页和筛选）"""
        try:
            # 构建查询
            query = db.session.query(School)
            
            # 应用筛选条件
            if province:
                query = query.filter(School.province == province)
            if city:
                query = query.filter(School.city == city)
            if school_type:
                query = query.filter(School.type == school_type)
            if is_985 is not None:
                query = query.filter(School.is_985 == is_985)
            if is_211 is not None:
                query = query.filter(School.is_211 == is_211)
            if is_double_first is not None:
                query = query.filter(School.is_double_first == is_double_first)
            if keyword:
                query = query.filter(
                    db.or_(
                        School.name.like(f'%{keyword}%'),
                        School.province.like(f'%{keyword}%'),
                        School.city.like(f'%{keyword}%'),
                        School.type.like(f'%{keyword}%')
                    )
                )
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            schools = query.order_by(School.id).offset((page - 1) * page_size).limit(page_size).all()
            
            # 转换为字典列表
            schools_data = []
            for school in schools:
                schools_data.append({
                    'id': school.id,
                    'name': school.name,
                    'code': school.code,
                    'province': school.province,
                    'city': school.city,
                    'type': school.type,
                    'is_985': school.is_985,
                    'is_211': school.is_211,
                    'is_double_first': school.is_double_first,
                    'founded_year': school.founded_year,
                    'description': school.description,
                    'website': school.website,
                    'logo': school.logo,
                    'phd_count': school.phd_count,
                    'master_count': school.master_count
                })
            
            return {
                'list': schools_data,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        except Exception as e:
            print(f"[ERROR] 获取高校列表失败：{e}")
            raise e
    
    @staticmethod
    def get_school_detail(school_id):
        """获取高校详情"""
        try:
            school = db.session.query(School).filter(School.id == school_id).first()
            
            if not school:
                return None
            
            return {
                'id': school.id,
                'name': school.name,
                'code': school.code,
                'province': school.province,
                'city': school.city,
                'type': school.type,
                'is_985': school.is_985,
                'is_211': school.is_211,
                'is_double_first': school.is_double_first,
                'founded_year': school.founded_year,
                'description': school.description,
                'website': school.website,
                'logo': school.logo,
                'phd_count': school.phd_count,
                'master_count': school.master_count,
                'created_at': school.created_at.isoformat() if school.created_at else None,
                'updated_at': school.updated_at.isoformat() if school.updated_at else None
            }
        except Exception as e:
            print(f"[ERROR] 获取高校详情失败：{e}")
            raise e
    
    @staticmethod
    def get_provinces():
        """获取所有省份列表"""
        try:
            provinces = db.session.query(distinct(School.province)).filter(
                School.province.isnot(None)
            ).order_by(School.province).all()
            
            return [p[0] for p in provinces if p[0]]
        except Exception as e:
            print(f"[ERROR] 获取省份列表失败：{e}")
            raise e
    
    @staticmethod
    def get_cities(province=None):
        """获取所有城市列表（可按省份筛选）"""
        try:
            # 查询城市，按省份分组
            if province:
                # 按省份筛选
                query = db.session.query(distinct(School.city)).filter(
                    School.city.isnot(None),
                    School.province == province
                ).order_by(School.city)
                cities = query.all()
                # 返回城市列表（带省份信息）
                return [{'province': province, 'city': c[0]} for c in cities if c[0]]
            else:
                # 查询所有城市
                query = db.session.query(School.province, School.city).filter(
                    School.city.isnot(None)
                ).order_by(School.province, School.city)
                cities = query.all()
                return [{'province': c[0], 'city': c[1]} for c in cities if c[1]]
        except Exception as e:
            print(f"[ERROR] 获取城市列表失败：{e}")
            raise e
    
    @staticmethod
    def get_types():
        """获取所有学校类型列表"""
        try:
            types = db.session.query(distinct(School.type)).filter(
                School.type.isnot(None)
            ).order_by(School.type).all()
            
            return [t[0] for t in types if t[0]]
        except Exception as e:
            print(f"[ERROR] 获取学校类型列表失败：{e}")
            raise e
    
    @staticmethod
    def get_school_provinces(school_id):
        """获取学校招生省份列表"""
        try:
            provinces = db.session.query(distinct(AdmRecord.province)).filter(
                AdmRecord.school_id == school_id,
                AdmRecord.province.isnot(None)
            ).order_by(AdmRecord.province).all()
            
            return [p[0] for p in provinces if p[0]]
        except Exception as e:
            print(f"[ERROR] 获取学校招生省份列表失败：{e}")
            raise e
    
    @staticmethod
    def get_school_majors(school_id, province):
        """获取学校在指定省份的专业列表"""
        try:
            majors = db.session.query(distinct(AdmRecord.major_name)).filter(
                AdmRecord.school_id == school_id,
                AdmRecord.province == province,
                AdmRecord.major_name.isnot(None)
            ).order_by(AdmRecord.major_name).all()
            
            return [m[0] for m in majors if m[0]]
        except Exception as e:
            print(f"[ERROR] 获取学校专业列表失败：{e}")
            raise e
    
    @staticmethod
    def get_school_scores(school_id, province, major):
        """获取学校专业分数线数据"""
        try:
            scores = db.session.query(
                AdmRecord.year,
                AdmRecord.min_score,
                AdmRecord.min_rank
            ).filter(
                AdmRecord.school_id == school_id,
                AdmRecord.province == province,
                AdmRecord.major_name == major
            ).order_by(AdmRecord.year).all()
            
            return [{
                'year': s.year,
                'min_score': s.min_score,
                'min_rank': s.min_rank
            } for s in scores]
        except Exception as e:
            print(f"[ERROR] 获取学校分数线数据失败：{e}")
            raise e
