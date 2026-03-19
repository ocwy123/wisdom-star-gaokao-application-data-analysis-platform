from pyhive import hive

try:
    conn = hive.Connection(
        host='192.168.54.241',
        port=10000,
        database='default',          # 先用默认库测试
        auth=None
    )
    cursor = conn.cursor()
    cursor.execute('show databases')
    databases = cursor.fetchall()
    print("连接成功，数据库列表：", databases)
    cursor.close()
    conn.close()
except Exception as e:
    print("连接失败：", e)