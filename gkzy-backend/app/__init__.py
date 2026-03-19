from flask import Flask
from app.config import Config
from app.extensions import db, cors, cache
from app.routes.school import school_bp
from app.routes.overview import overview_bp
from app.routes.heat import heat_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    cors.init_app(app)
    cache.init_app(app)

    app.register_blueprint(school_bp)
    app.register_blueprint(overview_bp)
    app.register_blueprint(heat_bp)

    return app
