from app import create_app
from app.services.recommendation import RecommendationService

app = create_app()
"""运行Flask应用程序"""
if __name__ == '__main__':
    # 启动时先训练/加载推荐模型（force=True可改为False，若不希望每次都重训）
    with app.app_context():
        try:
            RecommendationService.train_model(force=True)
            print('Recommendation model trained/loaded successfully.')
        except Exception as e:
            print('Failed to train recommendation model on startup:', str(e))

    app.run(debug=True, host='0.0.0.0', port=5000)