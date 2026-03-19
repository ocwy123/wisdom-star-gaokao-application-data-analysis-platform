from pyhive import hive
from app.config import Config

def get_hive_connection():
    conn = hive.Connection(
        host=Config.HIVE_HOST,
        port=Config.HIVE_PORT,
        database=Config.HIVE_DB,
<<<<<<< HEAD
        auth='NOSASL'  # 根据集群认证方式调整
=======
        username=Config.HIVE_USER or None,  # 空字符串转为 None
        password=Config.HIVE_PASSWORD or None,
        auth=None
>>>>>>> d542ff691db917f1a695eec4809a16ccd8426862
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
