from app.models.school import School
from app.models.major import Major
from app.models.adm_record import AdmRecord
from app.extensions import db
from sqlalchemy import func, distinct
from datetime import datetime
from sqlalchemy.orm import aliased


class OverviewService:
    @staticmethod
    def get_statistics():
        school_count = db.session.query(func.count(School.id)).scalar()
        major_count = db.session.query(func.count(Major.id)).scalar()
        record_count = db.session.query(func.count(AdmRecord.id)).scalar()
        province_count = db.session.query(func.count(distinct(School.province))).scalar()

        return {
            'school_count': school_count or 0,
            'major_count': major_count or 0,
            'record_count': record_count or 0,
            'province_count': province_count or 0,
            'updated_at': datetime.now().isoformat()
        }

    @staticmethod
    def get_school_rank(limit=10):
        from app.utils.hive_util import query_hive
        sql = f"""
            SELECT school_id, school_name, heat_score
            FROM ana_school_heat
            ORDER BY heat_score DESC
            LIMIT {limit}
        """
        try:
            columns, rows = query_hive(sql)
            result = [dict(zip(columns, row)) for row in rows]
            return result
        except Exception as e:
            print(f"查询高校热度排行失败：{e}")
            return []

    @staticmethod
    def get_hot_schools(limit=8):
        """从 MySQL 的 ana_school_heat 表获取热门院校及其详细信息"""
        try:
            # 使用 SQLAlchemy 查询 ana_school_heat 表，关联 edu_school 表
            from app.models.school import School
            from sqlalchemy import text
            
            # 构建 SQL 查询
            sql = text("""
                SELECT 
                    s.id, 
                    s.name, 
                    s.province, 
                    s.city, 
                    s.type, 
                    s.is_985, 
                    s.is_211,
                    h.heat_score
                FROM ana_school_heat h
                INNER JOIN edu_school s ON h.school_id = s.id
                ORDER BY h.heat_score DESC
                LIMIT :limit
            """)
            
            # 执行查询
            result = db.session.execute(sql, {'limit': limit}).fetchall()
            
            if not result:
                return []
            
            # 转换为字典列表
            schools = []
            for row in result:
                schools.append({
                    'id': row.id,
                    'name': row.name,
                    'province': row.province,
                    'city': row.city,
                    'type': row.type,
                    'is_985': bool(row.is_985) if row.is_985 is not None else False,
                    'is_211': bool(row.is_211) if row.is_211 is not None else False,
                    'heat_score': float(row.heat_score) if row.heat_score else 0
                })
            
            return schools
        except Exception as e:
            print(f"查询热门院校失败：{e}")
            return []

    @staticmethod
    def get_major_rank(limit=10):
        """从 MySQL 获取热门专业及其就业数据"""
        try:
            from sqlalchemy import text
            
            # 使用原生 SQL 查询，避免模型关系冲突
            sql = text("""
                SELECT 
                    m.id,
                    m.name,
                    m.code,
                    m.description,
                    me.avg_salary,
                    me.year
                FROM edu_major m
                INNER JOIN ana_major_employment me ON m.id = me.major_id
                ORDER BY me.avg_salary DESC
                LIMIT :limit
            """)
            
            result = db.session.execute(sql, {'limit': limit}).fetchall()
            
            if not result:
                print("[DEBUG] 查询结果为空")
                return []
            
            # 转换为字典列表
            majors = []
            for row in result:
                majors.append({
                    'id': row.id,
                    'name': row.name,
                    'code': row.code or '',
                    'description': row.description or '',
                    'avg_salary': row.avg_salary or 0,
                    'year': row.year
                })
            
            print(f"[DEBUG] 返回的专业数据：{majors}")
            return majors
        except Exception as e:
            print(f"[ERROR] 查询热门专业失败：{e}")
            import traceback
            traceback.print_exc()
            return []


    @staticmethod
    def get_score_trend(province=None, batch=None, years=5):
        from sqlalchemy import desc
        query = db.session.query(
            AdmRecord.year,
            func.avg(AdmRecord.min_score).label('avg_score'),
            func.min(AdmRecord.min_score).label('min_score'),
            func.max(AdmRecord.min_score).label('max_score')
        ).group_by(AdmRecord.year)

        if province:
            query = query.filter(AdmRecord.province == province)
        if batch:
            query = query.filter(AdmRecord.batch == batch)

        query = query.order_by(desc(AdmRecord.year)).limit(years)
        results = query.all()

        return [
            {
                'year': r.year,
                'avg_score': float(r.avg_score) if r.avg_score else 0,
                'min_score': r.min_score or 0,
                'max_score': r.max_score or 0
            }
            for r in results
        ]

    @staticmethod
    def get_province_difficulty():
        query = db.session.query(
            AdmRecord.province,
            func.avg(AdmRecord.min_score).label('avg_score'),
            func.count(AdmRecord.id).label('school_count')
        ).group_by(AdmRecord.province).order_by(func.avg(AdmRecord.min_score).desc())

        results = query.all()
        return [
            {
                'province': r.province,
                'avg_score': float(r.avg_score) if r.avg_score else 0,
                'school_count': r.school_count or 0
            }
            for r in results
        ]

    @staticmethod
    def get_plan_distribution(year=None):
        query = db.session.query(
            AdmRecord.province,
            func.sum(AdmRecord.plan_count).label('total_plan')
        )

        if year:
            query = query.filter(AdmRecord.year == year)

        query = query.group_by(AdmRecord.province).order_by(func.sum(AdmRecord.plan_count).desc())
        results = query.all()

        return [
            {
                'province': r.province,
                'total_plan': r.total_plan or 0
            }
            for r in results
        ]
