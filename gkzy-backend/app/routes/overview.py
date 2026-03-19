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
@cache.cached(timeout=600, key_prefix='score_trend')
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


@overview_bp.route('/plan-distribution', methods=['GET'])
@cache.cached(timeout=600, key_prefix='plan_distribution')
def get_plan_distribution():
    try:
        year = request.args.get('year', type=int)
        data = OverviewService.get_plan_distribution(year)
        return success(data=data)
    except Exception as e:
        return error(message=str(e)), 500
