from app.services.recommendation import RecommendationService
import os

# 删除旧模型文件，强制重新训练
model_path = 'app/models/recommendation_model.pkl'
if os.path.exists(model_path):
    os.remove(model_path)
encoder_path = model_path.replace('.pkl', '_encoder.pkl')
if os.path.exists(encoder_path):
    os.remove(encoder_path)

# 重新训练模型
try:
    model = RecommendationService.train_model(force=True)
    print('模型训练成功！')

    # 测试推荐功能
    result = RecommendationService.get_volunteer_recommendations(
        user_score=650,
        user_province='陕西',
        user_subject='计算机科学与技术'
    )
    print(f'冲刺院校数量: {len(result["rush"])}')
    print(f'稳妥院校数量: {len(result["stable"])}')
    print(f'保底院校数量: {len(result["safe"])}')

    if result['rush']:
        print(f'示例冲刺院校: {result["rush"][0]["name"]} (概率: {result["rush"][0]["probability"]})')

    if result['stable']:
        print(f'示例稳妥院校: {result["stable"][0]["name"]} (概率: {result["stable"][0]["probability"]})')

except Exception as e:
    print(f'训练失败: {e}')
    import traceback
    traceback.print_exc()