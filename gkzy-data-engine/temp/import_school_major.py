#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
脚本功能：将 data/school_major_data.csv 中的数据导入到 MySQL 数据库的 edu_school_major 表中。
数据库信息：
    host: 192.168.54.241
    port: 3306
    user: root
    password: root
    database: gkzy_mysql
表结构：
    edu_school_major (id, school_id, major_id, description, created_at, updated_at)
    edu_school (id, name)
    edu_major (id, name)
CSV 列：school_name, major_name, description
"""

import csv
import pymysql
from datetime import datetime
import sys
import os

# 数据库连接参数
DB_CONFIG = {
    'host': '192.168.54.241',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'gkzy_mysql',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor  # 使用字典游标方便获取字段名
}

# CSV 文件路径（相对于脚本所在目录的上一级 data 目录）
# 脚本位于 temp/ 下，data/ 与 temp/ 同级
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(BASE_DIR, 'data', 'school_major_data.csv')

# 批量插入的批次大小
BATCH_SIZE = 100

def get_school_id(cursor, school_name):
    """根据学校名称查询学校ID"""
    sql = "SELECT id FROM edu_school WHERE name = %s"
    cursor.execute(sql, (school_name,))
    result = cursor.fetchone()
    if result:
        return result['id']
    else:
        return None

def get_major_id(cursor, major_name):
    """根据专业名称查询专业ID"""
    sql = "SELECT id FROM edu_major WHERE name = %s"
    cursor.execute(sql, (major_name,))
    result = cursor.fetchone()
    if result:
        return result['id']
    else:
        return None

def main():
    # 检查 CSV 文件是否存在
    if not os.path.isfile(CSV_FILE):
        print(f"错误：CSV 文件不存在：{CSV_FILE}")
        sys.exit(1)

    # 连接数据库
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except pymysql.MySQLError as e:
        print(f"数据库连接失败：{e}")
        sys.exit(1)

    # 存储待插入的数据列表
    insert_data = []
    total_rows = 0
    inserted_rows = 0
    skipped_rows = 0
    missing_schools = set()
    missing_majors = set()

    # 读取 CSV 文件
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # 检查必要的列
            required_columns = {'school_name', 'major_name', 'description'}
            if not required_columns.issubset(reader.fieldnames):
                print(f"错误：CSV 文件缺少必要的列，需要：{required_columns}，实际：{reader.fieldnames}")
                sys.exit(1)

            for row in reader:
                total_rows += 1
                school_name = row['school_name'].strip()
                major_name = row['major_name'].strip()
                description = row['description'].strip() if row['description'] else ''

                # 查询学校ID
                school_id = get_school_id(cursor, school_name)
                if school_id is None:
                    missing_schools.add(school_name)
                    skipped_rows += 1
                    continue

                # 查询专业ID
                major_id = get_major_id(cursor, major_name)
                if major_id is None:
                    missing_majors.add(major_name)
                    skipped_rows += 1
                    continue

                # 准备插入数据
                now = datetime.now()
                insert_data.append((
                    school_id,
                    major_id,
                    description,
                    now,
                    now
                ))

                # 达到批次大小，执行批量插入
                if len(insert_data) >= BATCH_SIZE:
                    execute_batch_insert(cursor, insert_data)
                    inserted_rows += len(insert_data)
                    insert_data.clear()

        # 处理剩余数据
        if insert_data:
            execute_batch_insert(cursor, insert_data)
            inserted_rows += len(insert_data)

        # 提交事务
        conn.commit()
        print(f"处理完成：总行数={total_rows}, 成功插入={inserted_rows}, 跳过={skipped_rows}")
        if missing_schools:
            print(f"未找到的学校（共{len(missing_schools)}个）：{', '.join(sorted(missing_schools))}")
        if missing_majors:
            print(f"未找到的专业（共{len(missing_majors)}个）：{', '.join(sorted(missing_majors))}")

    except csv.Error as e:
        print(f"CSV 文件读取错误：{e}")
        conn.rollback()
    except pymysql.MySQLError as e:
        print(f"数据库操作错误：{e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def execute_batch_insert(cursor, data):
    """批量插入数据"""
    sql = """
        INSERT INTO edu_school_major 
        (school_id, major_id, description, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.executemany(sql, data)

if __name__ == '__main__':
    main()