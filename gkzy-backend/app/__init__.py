from flask import Flask, request
from flask import Flask
from flask_cors import CORS
from app.extensions import db, cors, cache
import pymysql
import os
from dotenv import load_dotenv
from app.middleware.cors import init_cors
from app.services.admin_auth import admin_auth_bp

# 加载 .env 文件
load_dotenv()

# 导入所有模型，确保 SQLAlchemy 能正确建立关系
from app.models.school import School
from app.models.major import Major
from app.models.school_major import SchoolMajor
from app.models.adm_record import AdmRecord
from app.models.major_employment import MajorEmployment
from app.models.user import User
from app.models.favorite import Favorite
from app.models.data_source import DataSource

# 注册蓝图
from app.routes.favorite import favorite_bp
from app.services.data_import import data_import_bp
from app.services.admin_auth import admin_auth_bp
from app.routes.auth import auth_bp
from app.routes.overview import overview_bp
from app.routes.school import school_bp
from app.services.analysis import analysis_bp
from app.routes.major import major_bp
from app.routes.recommendation import recommendation_bp

def create_app():
    app = Flask(__name__)
    
    # 从 .env 文件读取 CORS origins
    cors_origins_str = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173')
    cors_origins = [origin.strip() for origin in cors_origins_str.split(',')]
    
    CORS(app, origins=cors_origins, supports_credentials=True)
    init_cors(app)
    
    # 从 .env 文件读取 MySQL 配置
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT'))
    
    # 使用 PyMySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    # 添加连接参数
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': DB_CONNECT_TIMEOUT,
            'charset': 'utf8mb4'
        }
    }
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT 密钥从 .env 文件读取
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'NUWRghoxw_rT5sP60LTcO7PaLAoK3Zm8yHOMA-bkgs8')
    
    # 先测试连接
    try:
        # 直接测试连接
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            port=int(DB_PORT),
            database=DB_NAME,
            connect_timeout=DB_CONNECT_TIMEOUT
        )
        print("=" * 60)
        print("✅ 远程数据库连接测试成功！")
        conn.close()
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        print("\n请检查:")
        print("1. 远程服务器 MySQL 是否允许远程连接")
        print("2. 用户名密码是否正确")
        print("3. 防火墙是否开放 3306 端口")
        print("4. 数据库 'gkzy_mysql' 是否存在")
        print("=" * 60)
    
    # 初始化数据库
    db.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})

    # 初始化缓存
    cache.init_app(app)


    # 注册所有蓝图路由
    app.register_blueprint(admin_auth_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(overview_bp)
    app.register_blueprint(school_bp)
    app.register_blueprint(major_bp)
    app.register_blueprint(favorite_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommendation')
    app.register_blueprint(data_import_bp)

    @app.before_request
    def log_request():
        print(f"收到请求: {request.method} {request.path}")

    return app
