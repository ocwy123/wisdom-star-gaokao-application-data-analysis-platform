from app.models.school import School
from app.models.major import Major
from app.models.adm_record import AdmRecord
from app.extensions import db
from sqlalchemy import func, distinct
from datetime import datetime


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
    def get_major_rank(limit=10):
        from app.utils.hive_util import query_hive
        sql = f"""
            SELECT major_id, major_name, heat_score
            FROM ana_major_heat
            ORDER BY heat_score DESC
            LIMIT {limit}
        """
        try:
            columns, rows = query_hive(sql)
            result = [dict(zip(columns, row)) for row in rows]
            return result
        except Exception as e:
            print(f"查询专业热度排行失败：{e}")
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
