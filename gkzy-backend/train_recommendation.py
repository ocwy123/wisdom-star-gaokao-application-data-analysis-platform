from app import create_app
from app.services.recommendation import RecommendationService

app = create_app()

"""训练志愿推荐模型"""
if __name__ == '__main__':
    with app.app_context():
        try:
            RecommendationService.train_model(force=True)
            print('Recommendation model trained/loaded successfully.')
        except Exception as e:
            print('Failed to train recommendation model:', str(e))