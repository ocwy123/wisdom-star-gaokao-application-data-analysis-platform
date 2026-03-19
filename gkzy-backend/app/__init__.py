from flask import Flask
from flask_cors import CORS
from app.extensions import db
import mysql.connector
from mysql.connector import Error

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # MySQL 配置（远程）
    DB_USERNAME = 'root'
    DB_PASSWORD = 'root'
    DB_HOST = '192.168.54.241'
    DB_PORT = '3306'
    DB_NAME = 'gkzy_mysql'
    
    # 使用 mysql-connector-python
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    # 添加连接参数
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'use_pure': True,
            'connection_timeout': 10,
            'charset': 'utf8mb4',
            'use_unicode': True,
            'ssl_disabled': True
        }
    }
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT 密钥
    app.config['JWT_SECRET_KEY'] = 'NUWRghoxw_rT5sP60LTcO7PaLAoK3Zm8yHOMA-bkgs8'
    
    # 先测试连接
    try:
        # 直接测试连接
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            port=DB_PORT,
            database=DB_NAME,
            use_pure=True,
            connection_timeout=10
        )
        print("=" * 60)
        print("✅ 远程数据库连接测试成功！")
        conn.close()
    except Error as e:
        print(f"❌ 数据库连接测试失败: {e}")
        print("\n请检查:")
        print("1. 远程服务器 MySQL 是否允许远程连接")
        print("2. 用户名密码是否正确 (root/root)")
        print("3. 防火墙是否开放 3306 端口")
        print("4. 数据库 'gkzy_mysql' 是否存在")
        print("=" * 60)
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    from app.services.admin_auth import admin_auth_bp
    app.register_blueprint(admin_auth_bp)
    
    # 创建表
    with app.app_context():
        try:
            db.create_all()
            print("✅ 数据库表创建/检查完成")
        except Exception as e:
            print(f"⚠️ 创建表时出错: {e}")
    
    return app
