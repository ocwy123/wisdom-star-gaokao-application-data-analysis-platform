from pyhive import hive
from app.config import Config

def get_hive_connection():
    conn = hive.Connection(
        host=Config.HIVE_HOST,
        port=Config.HIVE_PORT,
        database=Config.HIVE_DB,
        username=Config.HIVE_USER or None,  # 空字符串转为 None
        password=Config.HIVE_PASSWORD or None,
        auth=None
    )
    return conn

def query_hive(sql):
    conn = get_hive_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return columns, result
