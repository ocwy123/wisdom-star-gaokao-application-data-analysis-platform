import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MySQL
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Hive
    HIVE_HOST = os.getenv('HIVE_HOST')
    HIVE_PORT = os.getenv('HIVE_PORT')
    HIVE_DB = os.getenv('HIVE_DB')
<<<<<<< HEAD
=======
    HIVE_USER = os.getenv('HIVE_USER')
    HIVE_PASSWORD = os.getenv('HIVE_PASSWORD')
>>>>>>> d542ff691db917f1a695eec4809a16ccd8426862

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
