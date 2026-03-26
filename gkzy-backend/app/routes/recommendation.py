from flask import Blueprint, request, jsonify
from app.services.recommendation import RecommendationService
from app.utils.response import success, error

recommendation_bp = Blueprint('recommendation', __name__)


@recommendation_bp.route('/volunteer', methods=['POST'])
def volunteer_recommendation():
    """
    志愿推荐接口
    请求体: {
        "score": 650,  // 用户高考分数
        "province": "北京",  // 用户所在省份
        "subject": "物理类",  // 选科类别：物理类、历史类、理科、文科、综合类
        "school_province": "北京",  // 可选，理想院校省份
        "school_type": "理工类"  // 可选，理想院校类型
    }
    """
    try:
        data = request.get_json()
        if not data:
            return error("请求体不能为空")

        # 必填参数验证
        required_fields = ['score', 'province', 'subject']
        for field in required_fields:
            if field not in data:
                return error(f"缺少必填参数: {field}")

        user_score = data['score']
        user_province = data['province']
        user_subject = data['subject']

        # 参数类型验证
        if not isinstance(user_score, int) or user_score < 0 or user_score > 750:
            return error("分数必须是0-750之间的整数")

        # 可选参数
        school_province = data.get('school_province')
        school_type = data.get('school_type')

        # 调用推荐服务
        result = RecommendationService.get_volunteer_recommendations(
            user_score=user_score,
            user_province=user_province,
            user_subject=user_subject,
            school_province=school_province,
            school_type=school_type
        )

        return success(result, "志愿推荐成功")

    except Exception as e:
        return error(f"志愿推荐失败: {str(e)}")


@recommendation_bp.route('/train', methods=['POST'])
def train_recommendation_model():
    """手动触发模型训练（用于更新模型、数据变更后调用）"""
    try:
        RecommendationService.train_model(force=True)
        return success(None, '推荐模型训练完成')
    except Exception as e:
        return error(f'推荐模型训练失败: {str(e)}')