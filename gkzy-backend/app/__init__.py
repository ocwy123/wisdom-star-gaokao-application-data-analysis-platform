from flask import Flask
from app.config import Config
from app.extensions import db, cors
# from app.routes.auth import auth_bp
from app.routes.school import school_bp
# from app.routes.overview import overview_bp
# ... 导入其他蓝图

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)
    # jwt.init_app(app)
    cors.init_app(app)

    # 注册蓝图
    # app.register_blueprint(auth_bp)
    app.register_blueprint(school_bp)
    # app.register_blueprint(overview_bp)
    # ...

    return app
