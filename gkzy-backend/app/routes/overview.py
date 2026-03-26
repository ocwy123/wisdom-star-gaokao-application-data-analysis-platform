from flask import Blueprint, request, jsonify
from app.extensions import cache
from app.services.overview import OverviewService
from app.utils.response import success, error

overview_bp = Blueprint('overview', __name__, url_prefix='/api/overview')


@overview_bp.route('/statistics', methods=['GET'])
@cache.cached(timeout=300, key_prefix='statistics')
def get_statistics():
    try:
        data = OverviewService.get_statistics()
        return success(data=data)
    except Exception as e:
        return error(message=str(e)), 500


@overview_bp.route('/school-rank', methods=['GET'])
@cache.cached(timeout=300, key_prefix='school_rank')
def get_school_rank():
    try:
        limit = request.args.get('limit', 10, type=int)
        data = OverviewService.get_school_rank(limit)
        return success(data=data)
    except Exception as e:
        return error(message=str(e)), 500


@overview_bp.route('/hot-schools', methods=['GET'])
@cache.cached(timeout=300, key_prefix='hot_schools')
def get_hot_schools():
    try:
        limit = request.args.get('limit', 8, type=int)
        data = OverviewService.get_hot_schools(limit)
        return success(data=data)
    except Exception as e:
        return error(message=str(e)), 500


@overview_bp.route('/major-rank', methods=['GET'])
@cache.cached(timeout=300, key_prefix='major_rank')
def get_major_rank():
    try:
        limit = request.args.get('limit', 10, type=int)
        data = OverviewService.get_major_rank(limit)
        return success(data=data)
    except Exception as e:
        return error(message=str(e)), 500


@overview_bp.route('/score-trend', methods=['GET'])
def get_score_trend():
    try:
        province = request.args.get('province')
        batch = request.args.get('batch')
        years = request.args.get('years', 5, type=int)
        data = OverviewService.get_score_trend(province, batch, years)
        return success(data=data)
    except Exception as e:
        return error(message=str(e)), 500


@overview_bp.route('/province-difficulty', methods=['GET'])
@cache.cached(timeout=600, key_prefix='province_difficulty')
def get_province_difficulty():
    try:
        data = OverviewService.get_province_difficulty()
        return success(data=data)
    except Exception as e:
        return error(message=str(e)), 500


@overview_bp.route('/score-segment', methods=['GET'])
def get_score_segment():
    try:
        province = request.args.get('province')
        year = request.args.get('year', type=int)
        subject = request.args.get('subject')
        data = OverviewService.get_score_segment(province, year, subject)
        return success(data=data)
    except Exception as e:
        return error(message=str(e)), 500


@overview_bp.route('/score-segment/options', methods=['GET'])
def get_score_segment_options():
    print("[ROUTE] 收到 /score-segment/options 请求")
    try:
        print("[ROUTE] 调用 OverviewService.get_score_segment_options()")
        data = OverviewService.get_score_segment_options()
        print(f"[ROUTE] 返回数据：{data}")
        return success(data=data)
    except Exception as e:
        print(f"[ROUTE] 错误：{e}")
        import traceback
        traceback.print_exc()
        return error(message=str(e)), 500
