from flask import Blueprint, jsonify
from app.utils.hive_util import query_hive
from app.utils.response import success, error

heat_bp = Blueprint('heat', __name__, url_prefix='/api/heat')

@heat_bp.route('/school', methods=['GET'])
def school_heat():
    sql = """
        SELECT school_id, school_name, heat_score
        FROM ana_school_heat
        ORDER BY heat_score DESC
        LIMIT 10
    """
    try:
        columns, rows = query_hive(sql)
        result = [dict(zip(columns, row)) for row in rows]
        return success(data=result)
    except Exception as e:
        return error(message=str(e)), 500