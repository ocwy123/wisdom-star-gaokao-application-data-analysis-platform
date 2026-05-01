#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
脚本名称：sync_school_heat.py
功能：将 edu_school 中的所有学校信息同步到 ana_school_heat 表中，
     为每个学校生成一条热度统计记录，并设置默认的搜索、收藏、浏览次数及热度指数。
作者：自动生成
日期：2026-03-24
"""

import pymysql
import sys
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'gkzy_mysql',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 默认值配置
DEFAULT_SEARCH_COUNT = 5000
DEFAULT_FAVORITE_COUNT = 1000
DEFAULT_VIEW_COUNT = 10000
DEFAULT_HEAT_SCORE = 50.00

def main():
    connection = None
    try:
        # 建立数据库连接
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        print("连接数据库成功，开始同步数据...")

        # 清空目标表（可选，根据需要决定是否保留已有数据）
        # 注意：如果表中有外键关联，需谨慎操作，此处假设无依赖
        print("清空 ana_school_heat 表...")
        cursor.execute("TRUNCATE TABLE ana_school_heat")
        # 或者使用 DELETE FROM ana_school_heat，但 TRUNCATE 更快

        # 查询所有学校的 id
        print("查询 edu_school 表中的所有学校...")
        cursor.execute("SELECT id FROM edu_school")
        schools = cursor.fetchall()

        if not schools:
            print("edu_school 表中没有数据，无需同步。")
            return

        # 准备批量插入的数据
        insert_sql = """
            INSERT INTO ana_school_heat
            (school_id, search_count, favorite_count, view_count, heat_score, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
        data = []
        for school in schools:
            data.append((
                school['id'],
                DEFAULT_SEARCH_COUNT,
                DEFAULT_FAVORITE_COUNT,
                DEFAULT_VIEW_COUNT,
                DEFAULT_HEAT_SCORE,
                now,
                now
            ))

        # 批量插入
        print(f"开始批量插入 {len(data)} 条记录...")
        cursor.executemany(insert_sql, data)
        connection.commit()

        print(f"同步完成，共插入 {len(data)} 条热度记录。")

    except pymysql.Error as e:
        print(f"数据库操作出错：{e}")
        if connection:
            connection.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"发生未知错误：{e}")
        sys.exit(1)
    finally:
        if connection:
            connection.close()
            print("数据库连接已关闭。")

if __name__ == "__main__":
    main()